# generator/sqlite_writer.py

import sqlite3
import json
from pathlib import Path

from schema import (
    CREATE_RAW_LOGS_TABLE
)

def init_db(db_path: Path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    cur.execute("PRAGMA temp_store=MEMORY;")

    cur.execute(CREATE_RAW_LOGS_TABLE)

    conn.commit()
    return conn


def insert_raw(
    conn,
    *,
    topic,
    tenant_id,
    line_id,
    process,
    device_type,
    metric,
    payload,
    received_at,
):
    cur = conn.cursor()
    cur.execute(
        """
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
        """,
        (
            topic,
            tenant_id,
            line_id,
            process,
            device_type,
            metric,
            json.dumps(payload, ensure_ascii=False),
            received_at,
        ),
    )

# payload: dict
# payload_json: serialized JSON string (single-encoded)
# payload = json.loads(payload_json)  # dict