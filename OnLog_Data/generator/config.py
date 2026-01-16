# generator/config.py

# =========================
# Tenant / Line
# =========================
TENANTS = [f"F{i:02d}" for i in range(1, 11)]
LINES = [f"L{i:02d}" for i in range(1, 5)]  # N = 4

# =========================
# Time
# =========================
INTERVAL_SEC = 10
START_TIME = "2026-01-16T00:00:00Z"
YEARS = 0.01

# =========================
# SQLite layout
# =========================
DB_ROOT_DIR = "C:\GitCode\CodeFolder\OnLog_Data\generator\data"

DB_SENSOR_ENV = "sensor_env.sqlite"
DB_SENSOR_SCALE = "sensor_scale.sqlite"
DB_MACHINE = "machine.sqlite"

RAW_LOG_TABLE = "raw_logs"

# =========================
# Logical Kafka Topics
# =========================
TOPIC_SENSOR_ENV = "sensor.env.raw"
TOPIC_SENSOR_SCALE = "sensor.scale.raw"
TOPIC_MACHINE = "machine.raw"
