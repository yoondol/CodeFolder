# generator/machine_generator.py

import uuid
import random
from datetime import datetime, timezone
import json


def _now():
    return datetime.now(timezone.utc).isoformat()


def generate_machine_payload(source):
    """
    source:
      process
      device_type
      metric
    """

    metric = source["metric"]

    if metric == "OIL_TEMP":
        value = round(random.uniform(160.0, 180.0), 1)

    elif metric == "ACID_VALUE":
        value = round(random.uniform(0.5, 2.5), 2)

    elif metric == "TEMP":
        value = round(random.uniform(20.0, 90.0), 1)

    elif metric == "HUMIDITY":
        value = round(random.uniform(20.0, 60.0), 1)

    elif metric == "FAN_SPEED":
        value = random.randint(800, 1600)

    elif metric == "CONVEYOR_SPEED":
        value = round(random.uniform(0.3, 1.2), 2)

    elif metric == "COOL_TIME":
        value = random.randint(30, 180)

    elif metric == "ENERGY_TOTAL":
        value = round(random.uniform(100000, 500000), 1)

    else:
        value = None

    # Boolean 계열
    if metric in ("OVERHEAT", "JAM_STATE", "METAL_DETECTED"):
        value = random.random() < 0.02  # rare event

    payload = {
        "eventTime": _now(),
        "device": {
            "tenantName": source["tenant_id"],
            "deviceType": source["device_type"],
            "deviceName": source["device_name"]
        },
        "metric": metric,
        "value": value,
        "unit": _infer_unit(metric)
    }

    return json.dumps(payload, ensure_ascii=False)


def _infer_unit(metric):
    return {
        "OIL_TEMP": "C",
        "TEMP": "C",
        "HUMIDITY": "%",
        "FAN_SPEED": "rpm",
        "CONVEYOR_SPEED": "m/s",
        "COOL_TIME": "sec",
        "ENERGY_TOTAL": "Wh"
    }.get(metric)
