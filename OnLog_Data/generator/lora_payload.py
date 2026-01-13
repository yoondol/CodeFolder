# generator/lora_payload.py

import struct
import base64

EXT_BYTES = bytes.fromhex("01 7f ff 7f ff")


def encode_payload(bat_status, voltage_mv, temperature, humidity):
    bat_raw = ((bat_status & 0b11) << 14) | (voltage_mv & 0x3FFF)
    bat_bytes = bat_raw.to_bytes(2, "big")

    temp_raw = int(round(temperature * 100))
    temp_bytes = struct.pack(">h", temp_raw)

    hum_raw = int(round(humidity * 10))
    hum_bytes = hum_raw.to_bytes(2, "big")

    payload = bat_bytes + temp_bytes + hum_bytes + EXT_BYTES
    return base64.b64encode(payload).decode()
