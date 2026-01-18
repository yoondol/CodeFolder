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
DEFAULT_END_DATE   = "2025-10-02"
BATCH_SIZE = 20000


# ======================================================
# CLI Args
# ======================================================
parser = argparse.ArgumentParser()
parser.add_argument("--sqlite", required=True, help="single sqlite file")
parser.add_argument("--start", default=DEFAULT_START_DATE)
parser.add_argument("--end",   default=DEFAULT_END_DATE)
parser.add_argument(
    "--pg-dsn",
    default="dbname=onlog user=ingest_user password=db host=localhost"
)
args = parser.parse_args()


# ======================================================
# Logging
# ======================================================
def log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


# ======================================================
# Helpers
# ======================================================
def make_source_id(factory, line, process, device, metric):
    return f"{factory}.{line}.{process}.{device}.{metric}"


def parse_payload(payload_json, path_name):
    try:
        return json.loads(payload_json)
    except Exception as e:
        raise RuntimeError(f"{path_name}: payload JSON decode failed: {e}")


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


# ======================================================
# Main ETL
# ======================================================
def process_sqlite(path: Path):
    log(f"START ETL: {path.name}")

    # SQLite
    conn = sqlite3.connect(path)
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
    """, (args.start, args.end))

    # Postgres
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

    batch = []
    total_rows = 0
    last_event_time = None
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

            payload = parse_payload(payload_json, path.name)
            device_name = extract_device_name(payload)
            last_event_time = received_at

            # ENV
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

            # SCALE
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

            # MACHINE
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
                    normalize_bool(payload.get("value_bool"))
                ))

            if len(batch) >= BATCH_SIZE:
                execute_batch(pg_cur, INSERT_SQL, batch)
                total_rows += len(batch)
                log(f"{path.name}: inserted {total_rows:,} rows (last={last_event_time})")
                batch.clear()

    except Exception as e:
        log(f"⚠️ STOPPED EARLY: {path.name}")
        log(f"⚠️ LAST EVENT TIME: {last_event_time}")
        log(str(e))

    # final flush (best effort)
    if batch:
        try:
            execute_batch(pg_cur, INSERT_SQL, batch)
            total_rows += len(batch)
        except Exception:
            pass

    elapsed = time.time() - t0
    log(f"END ETL: {path.name} | rows={total_rows:,} | {elapsed:.1f}s")

    conn.close()
    pg_cur.close()
    pg_conn.close()


# ======================================================
# Entry
# ======================================================
if __name__ == "__main__":
    sqlite_file = Path(args.sqlite)
    process_sqlite(sqlite_file)
    sys.exit(0)
