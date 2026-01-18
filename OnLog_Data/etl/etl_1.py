import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import time
import sys

import psycopg2
from psycopg2.extras import execute_batch


# ======================================================
# Config
# ======================================================
DEFAULT_START_DATE = "2025-10-01"
DEFAULT_END_DATE   = "2025-10-03"
BATCH_SIZE = 20000


# ======================================================
# CLI Args
# ======================================================
parser = argparse.ArgumentParser()
parser.add_argument("--data-dir", default="/mnt/d/onlog_data")
parser.add_argument("--start", default=DEFAULT_START_DATE)
parser.add_argument("--end",   default=DEFAULT_END_DATE)
parser.add_argument(
    "--pg-dsn",
    default="dbname=onlog user=ingest_user password=db host=localhost"
)
args = parser.parse_args()

START = datetime.fromisoformat(args.start)
END   = datetime.fromisoformat(args.end)


# ======================================================
# Logging
# ======================================================
def log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


# ======================================================
# Postgres
# ======================================================
pg_conn = psycopg2.connect(args.pg_dsn)
pg_conn.autocommit = True
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


def parse_payload(payload_json, path_name):
    """SQLite payload는 항상 TEXT(JSON string)"""
    try:
        return json.loads(payload_json)
    except Exception as e:
        raise RuntimeError(f"{path_name}: payload JSON decode failed: {e}")


def extract_device_name(payload):
    return (
        payload.get("deviceInfo", {}).get("deviceName")
        or payload.get("device", {}).get("deviceName")
    )


# ======================================================
# ETL per SQLite file
# ======================================================
def process_sqlite(path: Path):
    log(f"START ETL: {path.name}")

    conn = sqlite3.connect(path)
    cur = conn.cursor()

    # SQLite read optimization
    cur.execute("PRAGMA journal_mode=OFF;")
    cur.execute("PRAGMA synchronous=OFF;")
    cur.execute("PRAGMA temp_store=MEMORY;")

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

    for (
        received_at,
        factory_id,
        line_id,
        process,
        device_type,
        metric,
        payload_json
    ) in cur:

        payload = parse_payload(payload_json, path.name)
        device_name = extract_device_name(payload)

        # -------------------------
        # sensor_env → TEMP / HUMIDITY
        # -------------------------
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

        # -------------------------
        # sensor_scale → WEIGHT
        # -------------------------
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

        # -------------------------
        # machine
        # -------------------------
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

        # -------------------------
        # Batch flush
        # -------------------------
        if len(batch) >= BATCH_SIZE:
            log(f"FLUSH {path.name}: batch={len(batch)}")
            execute_batch(pg_cur, INSERT_SQL, batch)
            total_rows += len(batch)
            log(f"{path.name}: inserted {total_rows:,} rows")
            batch.clear()

    # Final flush
    if batch:
        log(f"FINAL FLUSH {path.name}: batch={len(batch)}")
        execute_batch(pg_cur, INSERT_SQL, batch)
        total_rows += len(batch)

    elapsed = time.time() - t0
    log(f"END ETL: {path.name} | rows={total_rows:,} | {elapsed:.1f}s")

    conn.close()


# ======================================================
# Run (FILE-LEVEL PROTECTION)
# ======================================================
data_dir = Path(args.data_dir)

log(f"ETL RANGE: {args.start} → {args.end}")
log(f"BATCH_SIZE = {BATCH_SIZE}")

for sqlite_file in sorted(data_dir.glob("F*_*.sqlite")):
    try:
        process_sqlite(sqlite_file)
    except Exception as e:
        log(f"❌ ERROR in {sqlite_file.name}")
        log(str(e))
        raise   # 원인 파악 후 계속 돌리고 싶으면 여기서 raise 제거

pg_cur.close()
pg_conn.close()

log("ALL ETL COMPLETED")
