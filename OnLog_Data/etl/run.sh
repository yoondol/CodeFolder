#!/bin/bash
set -e

if [ $# -ne 1 ]; then
  echo "Usage: ./run.sh <sqlite_file>"
  exit 1
fi

# ===============================
# 고정 설정
# ===============================
DATA_DIR="/mnt/d/onlog_data"
SQLITE_FILE="$DATA_DIR/$1"

START_DATE="2025-10-01"
END_DATE="2025-10-03"

if [ ! -f "$SQLITE_FILE" ]; then
  echo "File not found: $SQLITE_FILE"
  exit 1
fi

echo "===== $SQLITE_FILE ====="
python3 etl.py "$SQLITE_FILE" "$START_DATE" "$END_DATE"
