# generator/env_generator.py

import uuid
import json
import random
from sensor_state import SensorState
from time_utils import generate_times, dr_to_sf

# 주파수 풀 (8개)
FREQUENCIES = [
    921700000,
    922100000, 922300000, 922500000,
    922700000, 922900000, 923100000, 923300000,
]

# 센서 상태 캐시
SENSOR_STATES = {}


def _get_state(source):
    key = f"{source['tenant_id']}|{source['device_name']}"
    if key not in SENSOR_STATES:
        SENSOR_STATES[key] = SensorState(key)
    return SENSOR_STATES[key]


def generate_env_payload(source):
    state = _get_state(source)

    time, gw_time, ns_time, received_at = generate_times()

    dr = state.next_dr()
    sf = dr_to_sf(dr)

    payload = {
        "deduplicationId": str(uuid.uuid4()),
        "time": time,
        "deviceInfo": {
            "tenantName": source["tenant_id"],
            "applicationName": "EF-SmartFactory",
            "deviceProfileName": "LHT65N-KR920",
            "deviceName": source["device_name"],
            "devEui": state.dev_eui,
            "deviceClassEnabled": "CLASS_A",
            "tags": {}
        },
        "adr": True,
        "dr": dr,
        "fCnt": state.next_fcnt(),
        "fPort": 2,
        "confirmed": False,
        "data": "AAAA",  # payload 자체는 의미 없음
        "rxInfo": [
            {
                "gatewayId": "gw-ef-01",
                "gwTime": gw_time,
                "nsTime": ns_time,
                "rssi": state.next_rssi(),
                "snr": state.next_snr(),
                "crcStatus": "CRC_OK"
            }
        ],
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
        "regionConfigId": "kr920",
        "values": {
            "temperature": round(random.uniform(18, 28), 2),
            "humidity": round(random.uniform(30, 70), 2)
        }
    }

    return payload, received_at
