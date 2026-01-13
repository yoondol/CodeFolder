# generator/schema.py

CREATE_RAW_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS raw_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  -- =========================
  -- Time
  -- =========================
  received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- =========================
  -- Routing / Meta
  -- =========================
  topic TEXT NOT NULL,

  tenant_id TEXT NOT NULL,
  line_id TEXT,
  process TEXT,
  device_type TEXT,
  metric TEXT,

  -- =========================
  -- Raw Payload
  -- =========================
  payload TEXT NOT NULL
);
"""

CREATE_INDEX_TOPIC = """
CREATE INDEX IF NOT EXISTS idx_raw_logs_topic
ON raw_logs(topic);
"""

CREATE_INDEX_RECEIVED_AT = """
CREATE INDEX IF NOT EXISTS idx_raw_logs_received_at
ON raw_logs(received_at);
"""

CREATE_INDEX_TENANT_LINE = """
CREATE INDEX IF NOT EXISTS idx_raw_logs_tenant_line
ON raw_logs(tenant_id, line_id);
"""

CREATE_INDEX_PROCESS_METRIC = """
CREATE INDEX IF NOT EXISTS idx_raw_logs_process_metric
ON raw_logs(process, metric);
"""
