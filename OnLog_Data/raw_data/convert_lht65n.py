import base64
import struct
from datetime import datetime
import csv

INPUT_FILE = "lht65n08_raw.txt"
OUTPUT_FILE = "lht65n08_converted.csv"

def decode_lht65n_payload(b64: str):
    raw = base64.b64decode(b64)

    # LHT65N uplink payload = 11 bytes
    if len(raw) != 11:
        return None

    # BAT: uint16 (bit field)
    bat_raw = struct.unpack(">H", raw[0:2])[0]
    battery_mv = bat_raw & 0x3FFF  # lower 14 bits

    # Temperature: int16 / 100
    temp_raw = struct.unpack(">h", raw[2:4])[0]
    temperature_c = temp_raw / 100.0

    # Humidity: uint16 / 10
    hum_raw = struct.unpack(">H", raw[4:6])[0]
    humidity_pct = hum_raw / 10.0

    return battery_mv, temperature_c, humidity_pct

with open(INPUT_FILE, "r") as fin, open(OUTPUT_FILE, "w", newline="") as fout:
    writer = csv.writer(fout)
    writer.writerow([
        "time",
        "battery_mv",
        "temperature_c",
        "humidity_pct"
    ])

    count = 0

    for line in fin:
        line = line.strip()
        if not line:
            continue

        # "received_at","data"
        received_at, b64 = line.strip('"').split('","')

        decoded = decode_lht65n_payload(b64)
        if decoded is None:
            continue

        battery_mv, temperature_c, humidity_pct = decoded

        writer.writerow([
            received_at,
            battery_mv,
            temperature_c,
            humidity_pct
        ])

        count += 1

print(f"DONE: {count} rows written to {OUTPUT_FILE}")
