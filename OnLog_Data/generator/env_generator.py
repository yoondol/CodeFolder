# generator/env_generator.py

import uuid
import random
from datetime import datetime, timezone
import base64
import json


def _now():
    return datetime.now(timezone.utc).isoformat()


def _fake_base64():
    return base64.b64encode(random.randbytes(6)).decode()


def generate_env_payload(source):
    """
    source:
      tenant_id
      line_id
      process
      device_type
      device_name
      metrics = ["TEMP", "HUMIDITY"]
    """

    temperature = round(random.uniform(18.0, 28.0), 2)
    humidity = round(random.uniform(30.0, 70.0), 2)

    payload = {
        "deduplicationId": str(uuid.uuid4()),
        "time": _now(),
        "deviceInfo": {
            "tenantName": source["tenant_id"],
            "applicationName": "EF-SmartFactory",
            "deviceProfileName": "LHT65N-KR920",
            "deviceName": source["device_name"],
            "devEui": uuid.uuid4().hex[:16],
            "deviceClassEnabled": "CLASS_A",
            "tags": {}
        },
        "adr": True,
        "dr": random.choice([0, 1, 2, 3, 4, 5]),
        "fCnt": random.randint(1, 50000),
        "fPort": 2,
        "confirmed": False,
        "data": _fake_base64(),
        "rxInfo": [
            {
                "gatewayId": "gw-ef-01",
                "gwTime": _now(),
                "nsTime": _now(),
                "rssi": random.randint(-120, -60),
                "snr": round(random.uniform(-20, 10), 2),
                "crcStatus": "CRC_OK"
            }
        ],
        "txInfo": {
            "frequency": 922300000,
            "modulation": {
                "lora": {
                    "bandwidth": 125000,
                    "spreadingFactor": random.choice([7, 8, 9, 10, 11, 12]),
                    "codeRate": "CR_4_5"
                }
            }
        },
        "regionConfigId": "kr920",

        # === 실제 측정값 (TimescaleDB 파싱 대상) ===
        "values": {
            "temperature": temperature,
            "humidity": humidity
        }
    }

    return json.dumps(payload, ensure_ascii=False)
