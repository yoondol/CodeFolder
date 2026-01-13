# generator/run.py

from datetime import datetime, timedelta, timezone
from pathlib import Path

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
from sqlite_writer import init_db, insert_raw

UTC = timezone.utc


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

        sources = build_all_sources(tenant_id)

        t = start_time
        while t < end_time:
            for source in sources:

                # =========================
                # ENV
                # =========================
                if source["process"] == "ENV":
                    payload, received_at = generate_env_payload(source, t)
                    insert_raw(
                        env_db,
                        topic=TOPIC_SENSOR_ENV,
                        tenant_id=source["tenant_id"],
                        line_id=source["line_id"],
                        process=source["process"],
                        device_type=source["device_type"],
                        metric="ENV",
                        payload=payload,
                        received_at=received_at,
                    )

                # =========================
                # SCALE
                # =========================
                elif source["device_type"].endswith("_SCALE"):
                    payload, received_at = generate_scale_payload(source, t)
                    if payload:
                        insert_raw(
                            scale_db,
                            topic=TOPIC_SENSOR_SCALE,
                            tenant_id=source["tenant_id"],
                            line_id=source["line_id"],
                            process=source["process"],
                            device_type=source["device_type"],
                            metric="WEIGHT",
                            payload=payload,
                            received_at=received_at,
                        )

                # =========================
                # MACHINE / POWER
                # =========================
                else:
                    payload, received_at = generate_machine_payload(source, t)
                    insert_raw(
                        machine_db,
                        topic=TOPIC_MACHINE,
                        tenant_id=source["tenant_id"],
                        line_id=source["line_id"],
                        process=source["process"],
                        device_type=source["device_type"],
                        metric=source["metric"],
                        payload=payload,
                        received_at=received_at,
                    )

            t += step

        env_db.commit()
        scale_db.commit()
        machine_db.commit()

        env_db.close()
        scale_db.close()
        machine_db.close()

        print(f"[DONE] tenant={tenant_id}")


if __name__ == "__main__":
    run()
