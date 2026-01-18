#!/bin/bash
set -e

DATA_DIR="/mnt/d/onlog_data"

START_DATE="2025-10-01"
END_DATE="2026-03-05"

PREFIX="${1:-F}"

echo "=== ETL START ==="
echo "RANGE: $START_DATE → $END_DATE"
echo "PREFIX: $PREFIX"
echo

for SQLITE_FILE in "$DATA_DIR"/${PREFIX}*.sqlite; do
  if [ ! -f "$SQLITE_FILE" ]; then
    continue
  fi

  BASENAME=$(basename "$SQLITE_FILE")
  echo "===== $BASENAME ====="

  python3 etl.py "$SQLITE_FILE" "$START_DATE" "$END_DATE"
  RET=$?

  if [ $RET -eq 130 ]; then
    echo
    echo "[STOP] Interrupted by user. ETL halted."
    exit 130
  elif [ $RET -ne 0 ]; then
    echo
    echo "[ERROR] Failed on $BASENAME (exit code=$RET)"
    exit $RET
  fi

  echo
done

echo "=== ETL COMPLETED ==="
