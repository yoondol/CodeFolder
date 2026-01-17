#!/bin/bash
set -e

START=2025-10-01
END=2025-10-03

for f in /mnt/d/onlog_data/F*_*.sqlite; do
  echo "===== $f ====="
  python3 etl_one_sqlite.py \
    --sqlite "$f" \
    --start "$START" \
    --end "$END"
done
