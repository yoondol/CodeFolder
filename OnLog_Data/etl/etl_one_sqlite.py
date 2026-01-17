import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values


# ==============================
# Config
# ==============================
BATCH_SIZE = 20000


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


# ==============================
# Logging
# ==============================
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


# ==============================
# Helpers
# ==============================
def make_source_id(factory, line, process, device, metric):
    return f"{factory}.{line}.{process}.{device}.{metric}"


def parse_payload(s):
    return json.loads(s)


def extract_device_name(p):
    return (
        p.get("deviceInfo", {}).get("deviceName")
        or p.get("device", {}).get("deviceName")
    )


# ==============================
# Main
# ==============================
def main():
    sqlite_path = Path(args.sqlite)
    log(f"START FILE: {sqlite_path.name}")

    # SQLite
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("PRAGMA synchronous=OFF;")
    cur.execute("PRAGMA journal_mode=OFF;")
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

    # Postgres
    pg = psycopg2.connect(args.pg_dsn)
    pg.autocommit = True
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
    ) VALUES %s
    """

    total = 0
    batch = []

    while True:
        rows = cur.fetchmany(BATCH_SIZE)
        if not rows:
            break

        for (
            received_at,
            factory_id,
            line_id,
            process,
            device_type,
            metric,
            payload_json
        ) in rows:

            payload = parse_payload(payload_json)
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
                    payload.get("value_bool")
                ))

        execute_values(pg_cur, INSERT_SQL, batch)
        total += len(batch)
        log(f"{sqlite_path.name}: inserted {total:,}")
        batch.clear()

    # cleanup
    cur.close()
    conn.close()
    pg_cur.close()
    pg.close()

    log(f"END FILE: {sqlite_path.name} | total={total:,}")
    sys.exit(0)


if __name__ == "__main__":
    main()
