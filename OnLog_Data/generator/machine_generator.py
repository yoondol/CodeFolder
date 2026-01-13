# generator/machine_generator.py

import json
import random
from sensor_state import SensorState
from time_utils import generate_times

SENSOR_STATES = {}


def _get_state(source):
    key = f"{source['tenant_id']}|{source['device_name']}"
    if key not in SENSOR_STATES:
        SENSOR_STATES[key] = SensorState(key)
    return SENSOR_STATES[key]


def generate_machine_payload(source):
    state = _get_state(source)

    time, _, _, received_at = generate_times()

    metric = source["metric"]

    if metric in ("OVERHEAT", "JAM_STATE", "METAL_DETECTED"):
        value = random.random() < 0.01
    elif metric == "OIL_TEMP":
        value = round(random.uniform(165, 175), 1)
    elif metric == "ACID_VALUE":
        value = round(random.uniform(0.8, 1.8), 2)
    elif metric == "ENERGY_TOTAL":
        value = round(random.uniform(100000, 200000), 1)
    else:
        value = round(random.uniform(20, 80), 1)

    payload = {
        "eventTime": time,
        "devEui": state.dev_eui,
        "device": {
            "tenantName": source["tenant_id"],
            "deviceType": source["device_type"],
            "deviceName": source["device_name"]
        },
        "metric": metric,
        "value": value
    }

    return payload, received_at
