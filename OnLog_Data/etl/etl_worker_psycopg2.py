import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_batch


# ==============================
# Args
# ==============================
parser = argparse.ArgumentParser()
parser.add_argument("--sqlite", required=True)
parser.add_argument("--start", required=True)
parser.add_argument("--end", required=True)
parser.add_argument(
    "--pg-dsn",
    default="dbname=onlog user=ingest_user password=db host=localhost"
)
args = parser.parse_args()

BATCH = 20000


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def make_source_id(factory, line, process, device, metric):
    return f"{factory}.{line}.{process}.{device}.{metric}"


def extract_device_name(p):
    return (
        p.get("deviceInfo", {}).get("deviceName")
        or p.get("device", {}).get("deviceName")
    )


def normalize_bool(v):
    if v is True:
        return True
    if v is False:
        return False
    return None


def main():
    sqlite_path = Path(args.sqlite)
    log(f"START FILE {sqlite_path.name}")

    # SQLite
    conn = sqlite3.connect(sqlite_path)
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

    # Postgres
    pg = psycopg2.connect(args.pg_dsn)
    pg.autocommit = False   # ⭐ 핵심
    pg_cur = pg.cursor()

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
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    total = 0
    batch = []

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
        device_name = extract_device_name(payload)

        if "sensor_env" in sqlite_path.name:
            for m, v in [("TEMP", payload.get("temp")), ("HUMIDITY", payload.get("hum"))]:
                if v is None:
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
                    float(v),
                    None
                ))

        elif "sensor_scale" in sqlite_path.name:
            w = payload.get("values", {}).get("weight")
            if w is None:
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
                float(w),
                None
            ))

        elif "machine" in sqlite_path.name:
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
                normalize_bool(payload.get("value_bool"))
            ))

        if len(batch) >= BATCH:
            execute_batch(pg_cur, INSERT_SQL, batch)
            pg.commit()                 # ⭐ 반드시 commit
            total += len(batch)
            log(f"{sqlite_path.name}: inserted {total:,}")
            batch.clear()

    if batch:
        execute_batch(pg_cur, INSERT_SQL, batch)
        pg.commit()
        total += len(batch)
        log(f"{sqlite_path.name}: inserted {total:,}")

    log(f"END FILE {sqlite_path.name} total={total:,}")

    # ❗ connection close 전에 프로세스 종료
    sys.exit(0)


if __name__ == "__main__":
    main()
