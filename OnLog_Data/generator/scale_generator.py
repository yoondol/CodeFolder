# generator/scale_generator.py

import uuid
import random
from datetime import datetime, timezone
import base64
import json


def _now():
    return datetime.now(timezone.utc).isoformat()


def _fake_base64():
    return base64.b64encode(random.randbytes(4)).decode()


def generate_scale_payload(source):
    """
    source:
      device_type = DOUGH_SCALE | UNIT_SCALE | PACK_SCALE
      metric = WEIGHT
    """

    if source["device_type"] == "DOUGH_SCALE":
        weight = round(random.uniform(950.0, 1050.0), 1)

    elif source["device_type"] == "UNIT_SCALE":
        # 불량 일부 섞기
        if random.random() < 0.05:
            weight = round(random.uniform(11.0, 17.0), 2)
        else:
            weight = round(random.uniform(13.0, 15.0), 2)

    else:  # PACK_SCALE
        weight = round(random.uniform(4500.0, 5200.0), 1)

    payload = {
        "deduplicationId": str(uuid.uuid4()),
        "time": _now(),
        "deviceInfo": {
            "tenantName": source["tenant_id"],
            "applicationName": "EF-Scale",
            "deviceProfileName": source["device_type"],
            "deviceName": source["device_name"],
            "devEui": uuid.uuid4().hex[:16],
            "deviceClassEnabled": "CLASS_A",
            "tags": {}
        },
        "adr": True,
        "dr": random.choice([0, 1, 2, 3, 4, 5]),
        "fCnt": random.randint(1, 30000),
        "fPort": 8,
        "confirmed": False,
        "data": _fake_base64(),
        "rxInfo": [
            {
                "gatewayId": "gw-ef-01",
                "gwTime": _now(),
                "nsTime": _now(),
                "rssi": random.randint(-110, -85),
                "snr": round(random.uniform(-10, 10), 2),
                "crcStatus": "CRC_OK"
            }
        ],
        "regionConfigId": "kr920",

        "values": {
            "weight": weight
        }
    }

    return json.dumps(payload, ensure_ascii=False)
