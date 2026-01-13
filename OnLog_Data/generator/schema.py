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