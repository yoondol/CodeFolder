# generator/machine_generator.py

import random
from datetime import datetime, timedelta, timezone

from sensor_state import SensorState

KST = timezone(timedelta(hours=9))

# key: tenant|device → per-device state
SENSOR_STATES = {}


def _get_state(source):
    key = f"{source['tenant_id']}|{source['device_name']}"
    if key not in SENSOR_STATES:
        SENSOR_STATES[key] = {
            "radio": SensorState(key),
            "values": {},          # metric → last numeric value
            "events": {}           # metric → event_until
        }
    return SENSOR_STATES[key]


def generate_machine_payload(source, base_time, time_ctx):
    if base_time is None:
        base_time = datetime.now(timezone.utc)

    now_kst = base_time.astimezone(KST)

    state = _get_state(source)
    radio = state["radio"]
    metric = source["metric"]

    time = time_ctx["time"]
    received_at = time_ctx["received_at"]

    value = None
    value_bool = None

    values = state["values"]
    events = state["events"]

    # =========================
    # OVERHEAT (5분 지속)
    # =========================
    if metric == "OVERHEAT":
        until = events.get(metric)
        if until and now_kst < until:
            value_bool = True
        elif random.random() < 0.01:
            events[metric] = now_kst + timedelta(minutes=5)
            value_bool = True
        else:
            events.pop(metric, None)
            value_bool = False

    # =========================
    # JAM_STATE (2분 지속)
    # =========================
    elif metric == "JAM_STATE":
        until = events.get(metric)
        if until and now_kst < until:
            value_bool = True
        elif random.random() < 0.01:
            events[metric] = now_kst + timedelta(minutes=2)
            value_bool = True
        else:
            events.pop(metric, None)
            value_bool = False

    # =========================
    # METAL_DETECTED (순간 이벤트)
    # =========================
    elif metric == "METAL_DETECTED":
        value_bool = random.random() < 0.001

    # =========================
    # OIL_TEMP (연속)
    # =========================
    elif metric == "OIL_TEMP":
        base = values.get(metric, 165.0)
        value = round(base + random.uniform(-0.3, 0.3), 1)
        values[metric] = value

    # =========================
    # ACID_VALUE (상승 후 리셋)
    # =========================
    elif metric == "ACID_VALUE":
        base = values.get(metric, 0.9)
        base += random.uniform(0.0005, 0.002)
        if base >= 2.0:
            base = 0.9
        value = round(base, 3)
        values[metric] = value

    # =========================
    # COATER TEMP
    # =========================
    elif metric == "TEMP" and source["process"] == "COAT":
        base = values.get(metric, 70.0)
        value = round(base + random.uniform(-0.2, 0.2), 1)
        values[metric] = value

    # =========================
    # COOLER TEMP
    # =========================
    elif metric == "TEMP" and source["process"] == "COOL":
        base = values.get(metric, 20.0)
        value = round(base + random.uniform(-0.3, 0.3), 1)
        values[metric] = value

    # =========================
    # BRIX
    # =========================
    elif metric == "BRIX":
        base = values.get(metric, 75.0)
        value = round(base + random.uniform(-0.5, 0.5), 1)
        values[metric] = value

    # =========================
    # COOL_TIME (랜덤)
    # =========================
    elif metric == "COOL_TIME":
        base = values.get(metric, 200.0)
        if random.random() < 0.005:
            base = base + random.uniform(-5.0, 5.0)
        value = round(min(220.0, max(180.0, base)), 1)
        values[metric] = value

    # =========================
    # FAN_SPEED (고정 step)
    # =========================
    elif metric == "FAN_SPEED":
        if metric not in values:
            values[metric] = random.choice(range(1000, 1351, 50))
        value = values[metric]

    # =========================
    # HUMIDITY (bounded random walk)
    # =========================
    elif metric == "HUMIDITY":
        base = values.get(metric, random.uniform(25, 38))
        value = round(min(38, max(25, base + random.uniform(-0.3, 0.3))), 1)
        values[metric] = value

    # =========================
    # CONVEYOR_SPEED (고정)
    # =========================
    elif metric == "CONVEYOR_SPEED":
        if metric not in values:
            values[metric] = round(random.uniform(1.0, 1.4), 2)
        value = values[metric]

    # =========================
    # ENERGY_TOTAL (누적, 절대 감소 없음)
    # =========================
    elif metric == "ENERGY_TOTAL":
        base = values.get(metric, 5000.0)
        base += 3 / 360  # 10초 기준 증가량
        value = round(base, 2)
        values[metric] = value

    payload = {
        "eventTime": time,
        "devEui": radio.dev_eui,
        "device": {
            "tenantName": source["tenant_id"],
            "deviceType": source["device_type"],
            "deviceName": f"{source['tenant_id']}_{source['device_name']}"
        },
        "metric": metric,
        "value": value,
        "value_bool": value_bool
    }

    return payload, received_at
