import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_batch


# =========================
# CLI Args
# =========================
parser = argparse.ArgumentParser()
parser.add_argument("--data-dir", default="/mnt/d/onlog_data")
parser.add_argument("--start", required=True)  # YYYY-MM-DD
parser.add_argument("--end", required=True)    # YYYY-MM-DD
parser.add_argument("--pg-dsn", default="dbname=onlog user=postgres")
args = parser.parse_args()

START = datetime.fromisoformat(args.start)
END = datetime.fromisoformat(args.end)


# =========================
# Postgres
# =========================
pg_conn = psycopg2.connect(args.pg_dsn)
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


# =========================
# Helpers
# =========================
def within_range(ts: str) -> bool:
    t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return START <= t < END


def source_id(factory, line, process, device, metric):
    return f"{factory}.{line}.{process}.{device}.{metric}"


# =========================
# ETL per file
# =========================
def process_sqlite(path: Path):
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
        device_name = payload.get("deviceInfo", {}).get("deviceName")

        # -------------------------
        # sensor_env
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
                    source_id(factory_id, line_id, "ENV", "ENV_SENSOR", m),
                    device_name,
                    float(val),
                    None,
                    None
                ))

        # -------------------------
        # sensor_scale
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
                source_id(factory_id, line_id, "QC", device_type, "WEIGHT"),
                device_name,
                float(weight),
                None,
                None
            ))

        # -------------------------
        # machine
        # -------------------------
        elif "machine" in path.name:
            val = payload.get("value")
            val_bool = payload.get("value_bool")

            batch.append((
                received_at,
                factory_id,
                line_id,
                process,
                device_type,
                metric,
                source_id(factory_id, line_id, process, device_type, metric),
                payload.get("device", {}).get("deviceName"),
                val,
                val_bool,
                None
            ))

        if len(batch) >= 5000:
            execute_batch(pg_cur, INSERT_SQL, batch)
            pg_conn.commit()
            batch.clear()

    if batch:
        execute_batch(pg_cur, INSERT_SQL, batch)
        pg_conn.commit()

    conn.close()


# =========================
# Run
# =========================
data_dir = Path(args.data_dir)

for sqlite_file in sorted(data_dir.glob("F*_*.sqlite")):
    print(f"ETL: {sqlite_file.name}")
    process_sqlite(sqlite_file)

pg_cur.close()
pg_conn.close()
