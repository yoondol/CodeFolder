# generator/machine_generator.py

import random
from datetime import datetime, timedelta, timezone

from sensor_state import SensorState
from time_utils import generate_times

KST = timezone(timedelta(hours=9))

SENSOR_STATES = {}

def _get_state(source):
    key = f"{source['tenant_id']}|{source['device_name']}"
    if key not in SENSOR_STATES:
        SENSOR_STATES[key] = {
            "radio": SensorState(key),
            "value": None,
            "event_until": None
        }
    return SENSOR_STATES[key]


def generate_machine_payload(source, base_time: datetime | None = None):
    if base_time is None:
        base_time = datetime.now(timezone.utc)

    now_kst = base_time.astimezone(KST)

    state = _get_state(source)
    radio = state["radio"]
    metric = source["metric"]

    time, _, _, received_at = generate_times(base_time)

    value = None
    value_bool = None

    # =========================
    # OVERHEAT (5분 유지)
    # =========================
    if metric == "OVERHEAT":
        if state["event_until"] and now_kst < state["event_until"]:
            value_bool = True
        elif random.random() < 0.01:
            state["event_until"] = now_kst + timedelta(minutes=5)
            value_bool = True
        else:
            state["event_until"] = None
            value_bool = False

    # =========================
    # JAM_STATE (2분 유지)
    # =========================
    elif metric == "JAM_STATE":
        if state["event_until"] and now_kst < state["event_until"]:
            value_bool = True
        elif random.random() < 0.01:
            state["event_until"] = now_kst + timedelta(minutes=2)
            value_bool = True
        else:
            state["event_until"] = None
            value_bool = False

    # =========================
    # METAL_DETECTED (순간)
    # =========================
    elif metric == "METAL_DETECTED":
        value_bool = random.random() < 0.001

    # =========================
    # OIL_TEMP
    # =========================
    elif metric == "OIL_TEMP":
        base = state["value"] or 165.0
        value = round(base + random.uniform(-0.3, 0.3), 1)
        state["value"] = value

    # =========================
    # ACID_VALUE
    # =========================
    elif metric == "ACID_VALUE":
        base = state["value"] or 0.9
        base += random.uniform(0.0005, 0.002)
        if base >= 2.0:
            base = 0.9
        value = round(base, 3)
        state["value"] = value

    # =========================
    # COATER TEMP
    # =========================
    elif metric == "TEMP" and source["process"] == "COAT":
        base = state["value"] or 70.0
        value = round(base + random.uniform(-0.2, 0.2), 1)
        state["value"] = value

    # =========================
    # BRIX
    # =========================
    elif metric == "BRIX":
        base = state["value"] or 75.0
        value = round(base + random.uniform(-0.5, 0.5), 1)
        state["value"] = value

    # =========================
    # COOLER TEMP
    # =========================
    elif metric == "TEMP" and source["process"] == "COOL":
        base = state["value"] or 20.0
        value = round(base + random.uniform(-0.3, 0.3), 1)
        state["value"] = value

    # =========================
    # COOL_TIME
    # =========================
    elif metric == "COOL_TIME":
        value = round(random.uniform(180, 220), 1)

    # =========================
    # FAN_SPEED
    # =========================
    elif metric == "FAN_SPEED":
        if state["value"] is None:
            state["value"] = random.choice(range(1000, 1650, 50))
        value = state["value"]

    # =========================
    # DRY HUMIDITY
    # =========================
    elif metric == "HUMIDITY":
        base = state["value"] or random.uniform(25, 38)
        value = round(min(38, max(25, base + random.uniform(-0.3, 0.3))), 1)
        state["value"] = value

    # =========================
    # CONVEYOR SPEED
    # =========================
    elif metric == "CONVEYOR_SPEED":
        if state["value"] is None:
            state["value"] = round(random.uniform(1.0, 1.4), 2)
        value = state["value"]

    # =========================
    # ENERGY_TOTAL (누적)
    # =========================
    elif metric == "ENERGY_TOTAL":
        base = state["value"] or 5000.0
        base += 3 / 360  # 10초 기준 증가량
        value = round(base, 2)
        state["value"] = value

    payload = {
        "eventTime": time,
        "devEui": radio.dev_eui,
        "device": {
            "tenantName": source["tenant_id"],
            "deviceType": source["device_type"],
            "deviceName": source["device_name"]
        },
        "metric": metric,
        "value": value,
        "value_bool": value_bool
    }

    return payload, received_at
