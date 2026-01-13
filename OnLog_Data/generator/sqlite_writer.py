# generator/sqlite_writer.py

import sqlite3
import json
from pathlib import Path

from schema import (
    CREATE_RAW_LOGS_TABLE,
    CREATE_INDEX_TOPIC,
    CREATE_INDEX_RECEIVED_AT,
    CREATE_INDEX_TENANT_LINE,
    CREATE_INDEX_PROCESS_METRIC,
)

def init_db(db_path: Path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(CREATE_RAW_LOGS_TABLE)
    cur.execute(CREATE_INDEX_TOPIC)
    cur.execute(CREATE_INDEX_RECEIVED_AT)
    cur.execute(CREATE_INDEX_TENANT_LINE)
    cur.execute(CREATE_INDEX_PROCESS_METRIC)

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
            json.dumps(payload),
            received_at,
        ),
    )

# payload: dict
# payload_json: serialized JSON string (single-encoded)
# payload = json.loads(payload_json)  # dict