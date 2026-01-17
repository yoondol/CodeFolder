import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import time

import psycopg2
from psycopg2.extras import execute_batch


# ======================================================
# Config (DEFAULTS)
# ======================================================
DEFAULT_START_DATE = "2025-10-01"
DEFAULT_END_DATE   = "2025-10-03"
BATCH_SIZE = 20000   # ★ 튜닝 포인트


# ======================================================
# CLI Args
# ======================================================
parser = argparse.ArgumentParser()
parser.add_argument("--data-dir", default="/mnt/d/onlog_data")
parser.add_argument("--start", default=DEFAULT_START_DATE)  # YYYY-MM-DD
parser.add_argument("--end",   default=DEFAULT_END_DATE)    # YYYY-MM-DD
parser.add_argument("--pg-dsn", default="dbname=onlog user=ingest_user password=db host=localhost")
args = parser.parse_args()

START = datetime.fromisoformat(args.start)
END   = datetime.fromisoformat(args.end)


# ======================================================
# Postgres
# ======================================================
pg_conn = psycopg2.connect(args.pg_dsn)
pg_conn.autocommit = False
pg_cur = pg_conn.cursor()

INSERT_SQL = """
INSERT INTO raw_event (
  event_time,
  factory_id,
  line_id,
  process,
  device_type,
  metric,
  source_id,
  device_name,
  value_num,
  value_bool
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""


# ======================================================
# Helpers
# ======================================================
def make_source_id(factory, line, process, device, metric):
    return f"{factory}.{line}.{process}.{device}.{metric}"


def log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


# ======================================================
# ETL per SQLite file
# ======================================================
def process_sqlite(path: Path):
    log(f"START ETL: {path.name}")

    conn = sqlite3.connect(path)
    cur = conn.cursor()

    cur.execute("""
      SELECT
        received_at,
        tenant_id,
        line_id,
        process,
        device_type,
        metric,
        payload
      FROM raw_logs
      WHERE received_at >= ?
        AND received_at < ?
    """, (args.start, args.end))

    batch = []
    total_rows = 0
    t0 = time.time()

    try:
        for (
            received_at,
            factory_id,
            line_id,
            process,
            device_type,
            metric,
            payload_json
        ) in cur:

            payload = json.loads(payload_json)
            device_name = (
                payload.get("deviceInfo", {}).get("deviceName")
                or payload.get("device", {}).get("deviceName")
            )

            if "sensor_env" in path.name:
                for m, val in [
                    ("TEMP", payload.get("temp")),
                    ("HUMIDITY", payload.get("hum")),
                ]:
                    if val is None:
                        continue

                    batch.append((
                        received_at,
                        factory_id,
                        line_id,
                        "ENV",
                        "ENV_SENSOR",
                        m,
                        make_source_id(factory_id, line_id, "ENV", "ENV_SENSOR", m),
                        device_name,
                        float(val),
                        None
                    ))

            elif "sensor_scale" in path.name:
                weight = payload.get("values", {}).get("weight")
                if weight is None:
                    continue

                batch.append((
                    received_at,
                    factory_id,
                    line_id,
                    "QC",
                    device_type,
                    "WEIGHT",
                    make_source_id(factory_id, line_id, "QC", device_type, "WEIGHT"),
                    device_name,
                    float(weight),
                    None
                ))

            elif "machine" in path.name:
                batch.append((
                    received_at,
                    factory_id,
                    line_id,
                    process,
                    device_type,
                    metric,
                    make_source_id(factory_id, line_id, process, device_type, metric),
                    device_name,
                    payload.get("value"),
                    payload.get("value_bool")
                ))

            if len(batch) >= BATCH_SIZE:
                execute_batch(pg_cur, INSERT_SQL, batch)
                total_rows += len(batch)
                log(f"{path.name}: inserted {total_rows:,} rows")
                batch.clear()

        if batch:
            execute_batch(pg_cur, INSERT_SQL, batch)
            total_rows += len(batch)

        pg_conn.commit()        # ★ 파일 단위 commit

        elapsed = time.time() - t0
        log(f"END ETL: {path.name} | rows={total_rows:,} | {elapsed:.1f}s")

    except Exception as e:
        pg_conn.rollback()      # ★ 실패 시 롤백
        raise

    finally:
        cur.close()             # ★ 반드시 닫기
        conn.close()



# ======================================================
# Run
# ======================================================
data_dir = Path(args.data_dir)

log(f"ETL RANGE: {args.start} → {args.end}")
log(f"BATCH_SIZE = {BATCH_SIZE}")

for sqlite_file in sorted(data_dir.glob("F*_*.sqlite")):
    process_sqlite(sqlite_file)

pg_cur.close()
pg_conn.close()

log("ALL ETL COMPLETED")
