#!/bin/bash
set -e

if [ $# -ne 1 ]; then
  echo "Usage: ./run.sh <sqlite_file>"
  exit 1
fi

SQLITE_FILE="$1"

# ===============================
# ETL 기간 (여기서만 관리)
# ===============================
START_DATE="2025-10-01"
END_DATE="2025-10-03"

python3 etl.py \
  "$SQLITE_FILE" \
  "$START_DATE" \
  "$END_DATE"
