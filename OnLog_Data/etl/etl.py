import sys
import json
import sqlite3
import signal
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_batch


# ===============================
# Config
# ===============================
BATCH_SIZE = 100000
PG_DSN = "dbname=onlog user=ingest_user password=db host=localhost"


# ===============================
# Ctrl+C handling
# ===============================
STOP_REQUESTED = False


def handle_sigint(signum, frame):
    global STOP_REQUESTED
    STOP_REQUESTED = True
    print("\n[CTRL+C] Stop requested. Finishing current batch...", flush=True)


signal.signal(signal.SIGINT, handle_sigint)


# ===============================
# Logging
# ===============================
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


# ===============================
# Helpers
# ===============================
def make_source_id(factory, line, process, device, metric):
    return f"{factory}.{line}.{process}.{device}.{metric}"


def extract_device_name(payload):
    return (
        payload.get("deviceInfo", {}).get("deviceName")
        or payload.get("device", {}).get("deviceName")
    )


def normalize_bool(v):
    if v is True:
        return True
    if v is False:
        return False
    return None


# ===============================
# Main
# ===============================
def main():
    if len(sys.argv) != 4:
        print("Usage: python3 etl.py <sqlite_path> <start_date> <end_date>")
        sys.exit(1)

    sqlite_path = Path(sys.argv[1])
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    log(f"START FILE: {sqlite_path.name}")
    log(f"RANGE: {start_date} → {end_date}")

    # SQLite
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

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
    """, (start_date, end_date))

    # Postgres
    pg_conn = psycopg2.connect(PG_DSN)
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

    batch = []
    total = 0
    last_event_time = None

    for row in cur:
        if STOP_REQUESTED:
            break

        (
            received_at,
            factory_id,
            line_id,
            process,
            device_type,
            metric,
            payload_json
        ) = row

        payload = json.loads(payload_json)
        device_name = extract_device_name(payload)
        last_event_time = received_at

        if "sensor_env" in sqlite_path.name:
            for m, v in [("TEMP", payload.get("temp")),
                         ("HUMIDITY", payload.get("hum"))]:
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

        if len(batch) >= BATCH_SIZE:
            execute_batch(pg_cur, INSERT_SQL, batch)
            total += len(batch)
            log(f"{sqlite_path.name}: inserted {total:,} (last={last_event_time})")
            batch.clear()

    if batch and not STOP_REQUESTED:
        execute_batch(pg_cur, INSERT_SQL, batch)
        total += len(batch)

    if STOP_REQUESTED:
        log(f"STOPPED BY USER at event_time={last_event_time}")
        log(f"TOTAL INSERTED: {total:,}")
        sys.exit(130)
    else:
        log(f"COMPLETED FILE {sqlite_path.name}")
        log(f"TOTAL INSERTED: {total:,}")
        sys.exit(0)

    log(f"TOTAL INSERTED: {total:,}")

    conn.close()
    pg_cur.close()
    pg_conn.close()


if __name__ == "__main__":
    main()
