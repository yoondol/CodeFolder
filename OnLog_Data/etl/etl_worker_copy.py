import argparse
import json
import sqlite3
import tempfile
import sys
from datetime import datetime
from pathlib import Path

import psycopg2


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


def main():
    sqlite_path = Path(args.sqlite)
    log(f"START FILE {sqlite_path.name}")

    # SQLite
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=OFF;")
    cur.execute("PRAGMA synchronous=OFF;")

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

    total = 0

    while True:
        rows = cur.fetchmany(BATCH)
        if not rows:
            break

        with tempfile.NamedTemporaryFile(mode="w+") as tmp:
            batch_rows = 0

            for (
                received_at,
                factory_id,
                line_id,
                process,
                device_type,
                metric,
                payload_json
            ) in rows:

                payload = json.loads(payload_json)
                device_name = extract_device_name(payload)

                if "sensor_env" in sqlite_path.name:
                    for m, v in [("TEMP", payload.get("temp")), ("HUMIDITY", payload.get("hum"))]:
                        if v is None:
                            continue
                        tmp.write(
                            f"{received_at}\t{factory_id}\t{line_id}\tENV\tENV_SENSOR\t{m}\t"
                            f"{make_source_id(factory_id, line_id, 'ENV', 'ENV_SENSOR', m)}\t"
                            f"{device_name}\t{float(v)}\t\\N\n"
                        )
                        batch_rows += 1

                elif "sensor_scale" in sqlite_path.name:
                    w = payload.get("values", {}).get("weight")
                    if w is None:
                        continue
                    tmp.write(
                        f"{received_at}\t{factory_id}\t{line_id}\tQC\t{device_type}\tWEIGHT\t"
                        f"{make_source_id(factory_id, line_id, 'QC', device_type, 'WEIGHT')}\t"
                        f"{device_name}\t{float(w)}\t\\N\n"
                    )
                    batch_rows += 1

                elif "machine" in sqlite_path.name:
                    tmp.write(
                        f"{received_at}\t{factory_id}\t{line_id}\t{process}\t{device_type}\t{metric}\t"
                        f"{make_source_id(factory_id, line_id, process, device_type, metric)}\t"
                        f"{device_name}\t{payload.get('value')}\t{payload.get('value_bool')}\n"
                    )
                    batch_rows += 1

            tmp.flush()
            tmp.seek(0)

            pg_cur.copy_from(
                tmp,
                "raw_event",
                columns=(
                    "event_time",
                    "factory_id",
                    "line_id",
                    "process",
                    "device_type",
                    "metric",
                    "source_id",
                    "device_name",
                    "value_num",
                    "value_bool"
                ),
                null="\\N"
            )

            total += batch_rows
            log(f"{sqlite_path.name}: inserted {total:,}")

    cur.close()
    conn.close()
    pg_cur.close()
    pg.close()

    log(f"END FILE {sqlite_path.name}")
    sys.exit(0)


if __name__ == "__main__":
    main()
