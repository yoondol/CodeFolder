# generator/env_generator.py

import uuid
import random
from datetime import datetime, timezone

from sensor_state import SensorState
from env_model import generate_env_value
from battery_model import BatteryState
from lora_payload import encode_payload
from time_utils import generate_times, dr_to_sf

FREQUENCIES = [
    921700000,
    922100000, 922300000, 922500000,
    922700000, 922900000, 923100000, 923300000,
]

STATES = {}

def _sensor_key(source):
    return f"{source['tenant_id']}|{source['device_name']}"

def _get_state(source):
    key = _sensor_key(source)
    if key not in STATES:
        STATES[key] = {
            "radio": SensorState(key),
            "battery": BatteryState(),
            "env": None
        }
    return STATES[key]

def _infer_sensor_no(device_name: str) -> int:
    # 예: L01_ENV_3 → 3, WAREHOUSE_ENV_2 → 2
    raw = int(device_name.split("_")[-1])
    return ((raw - 1) % 12) + 1

def generate_env_payload(source, base_time, time_ctx):
    state = _get_state(source)

    if base_time is None:
        base_time = datetime.now(timezone.utc)

    sensor_no = _infer_sensor_no(source["device_name"])

    # ===== 환경 값 생성 =====
    temp, hum = generate_env_value(sensor_no, base_time, state["env"])
    state["env"] = {"temp": temp, "hum": hum}

    # ===== 배터리 =====
    voltage = state["battery"].next()
    bat_status = state["battery"].status()

    # ===== LoRa payload =====
    data_b64 = encode_payload(bat_status, voltage, temp, hum)

    # ===== Time & Radio =====
    time = time_ctx["time"]
    gw_time = time_ctx["gw_time"]
    ns_time = time_ctx["ns_time"]
    received_at = time_ctx["received_at"]
    
    dr = state["radio"].next_dr()
    sf = dr_to_sf(dr)

    payload = {
        "deduplicationId": str(uuid.uuid4()),
        "time": time,
        "deviceInfo": {
            "tenantName": source["tenant_id"],
            "applicationName": "EF-SmartFactory",
            "deviceProfileName": "LHT65N-KR920",
            "deviceName": f"{source['tenant_id']}_{source['device_name']}",
            "devEui": state["radio"].dev_eui,
            "deviceClassEnabled": "CLASS_A"
        },
        "adr": True,
        "dr": dr,
        "fCnt": state["radio"].next_fcnt(),
        "fPort": 2,
        "confirmed": False,
        "data": data_b64,
        "rxInfo": [{
            "gatewayId": "gw-ef-01",
            "gwTime": gw_time,
            "nsTime": ns_time,
            "rssi": state["radio"].next_rssi(),
            "snr": state["radio"].next_snr(),
            "crcStatus": "CRC_OK"
        }],
        "txInfo": {
            "frequency": random.choice(FREQUENCIES),
            "modulation": {
                "lora": {
                    "bandwidth": 125000,
                    "spreadingFactor": sf,
                    "codeRate": "CR_4_5"
                }
            }
        },
        "regionConfigId": "kr920"
    }

    return payload, received_at
