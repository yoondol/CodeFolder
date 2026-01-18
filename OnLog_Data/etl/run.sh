#!/bin/bash

START=2025-10-01
END=2026-10-02

for f in /mnt/d/onlog_data/F*_*.sqlite; do
  echo "===== $f ====="
  python3 etl_5.py \
    --sqlite "$f" \
    --start "$START" \
    --end "$END"
done
