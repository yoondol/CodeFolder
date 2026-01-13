# generator/run.py

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
from tqdm import tqdm
import orjson
from time_utils import generate_times

from config import (
    TENANTS,
    START_TIME,
    YEARS,
    INTERVAL_SEC,
    DB_ROOT_DIR,
    DB_SENSOR_ENV,
    DB_SENSOR_SCALE,
    DB_MACHINE,
    TOPIC_SENSOR_ENV,
    TOPIC_SENSOR_SCALE,
    TOPIC_MACHINE,
)
from meta import build_all_sources
from env_generator import generate_env_payload
from scale_generator import generate_scale_payload
from machine_generator import generate_machine_payload
from sqlite_writer import init_db

UTC = timezone.utc

BATCH_SIZE = 1000

INSERT_SQL = """
INSERT INTO raw_logs (
    topic,
    tenant_id,
    line_id,
    process,
    device_type,
    metric,
    payload,
    received_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""


def run():
    start_time = datetime.fromisoformat(START_TIME.replace("Z", "+00:00"))
    end_time = start_time + timedelta(days=365 * YEARS)
    step = timedelta(seconds=INTERVAL_SEC)

    db_root = Path(DB_ROOT_DIR)
    db_root.mkdir(parents=True, exist_ok=True)

    for tenant_id in TENANTS:
        print(f"[START] tenant={tenant_id}")

        env_db = init_db(db_root / f"{tenant_id}_{DB_SENSOR_ENV}")
        scale_db = init_db(db_root / f"{tenant_id}_{DB_SENSOR_SCALE}")
        machine_db = init_db(db_root / f"{tenant_id}_{DB_MACHINE}")

        env_cur = env_db.cursor()
        scale_cur = scale_db.cursor()
        machine_cur = machine_db.cursor()

        env_buf = []
        scale_buf = []
        machine_buf = []

        sources = build_all_sources(tenant_id)

        total_steps = int((end_time - start_time).total_seconds() / INTERVAL_SEC)

        t = start_time

        with tqdm(total=total_steps, desc=f"Generating {tenant_id}", unit="step") as pbar:
            while t < end_time:
                time_iso, gw_time, ns_time, received_at = generate_times(t)

                time_ctx = {
                    "time": time_iso,
                    "gw_time": gw_time,
                    "ns_time": ns_time,
                    "received_at": received_at,
                }

                for source in sources:

                    # =========================
                    # ENV
                    # =========================
                    if source["process"] == "ENV":
                        payload, received_at = generate_env_payload(source, t, time_ctx)
                        env_buf.append((
                            TOPIC_SENSOR_ENV,
                            source["tenant_id"],
                            source["line_id"],
                            source["process"],
                            source["device_type"],
                            "ENV",
                            orjson.dumps(payload).decode(),
                            received_at,
                        ))

                        if len(env_buf) >= BATCH_SIZE:
                            env_cur.executemany(INSERT_SQL, env_buf)
                            env_db.commit()
                            env_buf.clear()

                    # =========================
                    # SCALE
                    # =========================
                    elif source["device_type"].endswith("_SCALE"):
                        payload, received_at = generate_scale_payload(source, t, time_ctx)
                        if payload is not None:
                            scale_buf.append((
                                TOPIC_SENSOR_SCALE,
                                source["tenant_id"],
                                source["line_id"],
                                source["process"],
                                source["device_type"],
                                "WEIGHT",
                                orjson.dumps(payload).decode(),
                                received_at,
                            ))

                            if len(scale_buf) >= BATCH_SIZE:
                                scale_cur.executemany(INSERT_SQL, scale_buf)
                                scale_db.commit()
                                scale_buf.clear()

                    # =========================
                    # MACHINE
                    # =========================
                    else:
                        payload, received_at = generate_machine_payload(source, t, time_ctx)
                        machine_buf.append((
                            TOPIC_MACHINE,
                            source["tenant_id"],
                            source["line_id"],
                            source["process"],
                            source["device_type"],
                            source["metric"],
                            orjson.dumps(payload).decode(),
                            received_at,
                        ))

                        if len(machine_buf) >= BATCH_SIZE:
                            machine_cur.executemany(INSERT_SQL, machine_buf)
                            machine_db.commit()
                            machine_buf.clear()

                t += step
                pbar.update(1)

        # ===== flush remaining =====
        if env_buf:
            env_cur.executemany(INSERT_SQL, env_buf)
            env_db.commit()

        if scale_buf:
            scale_cur.executemany(INSERT_SQL, scale_buf)
            scale_db.commit()

        if machine_buf:
            machine_cur.executemany(INSERT_SQL, machine_buf)
            machine_db.commit()

        env_db.close()
        scale_db.close()
        machine_db.close()

        print(f"[DONE] tenant={tenant_id}")


if __name__ == "__main__":
    run()
