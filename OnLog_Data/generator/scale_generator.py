# generator/scale_generator.py

import uuid
import random
from datetime import datetime, timedelta, timezone

from sensor_state import SensorState
from time_utils import generate_times, dr_to_sf

# =========================
# LoRa Frequencies
# =========================
FREQUENCIES = [
    921700000,
    922100000, 922300000, 922500000,
    922700000, 922900000, 923100000, 923300000,
]

# =========================
# Time
# =========================
KST = timezone(timedelta(hours=9))

# =========================
# State Cache
# =========================
SENSOR_STATES = {}

def _get_state(source):
    key = f"{source['tenant_id']}|{source['device_name']}"
    if key not in SENSOR_STATES:
        SENSOR_STATES[key] = {
            "radio": SensorState(key),
            "last_event_time": None,
            "was_in_production": False
        }
    return SENSOR_STATES[key]


def _in_production_time(now_kst: datetime) -> bool:
    return 8 <= now_kst.hour < 21


def generate_scale_payload(source, base_time, time_ctx):
    """
    base_time: UTC datetime (외부에서 주입 가능)
    """
    if base_time is None:
        base_time = datetime.now(timezone.utc)

    now_kst = base_time.astimezone(KST)

    state = _get_state(source)
    radio = state["radio"]

    # ===== Time (외부에서 주입) =====
    time = time_ctx["time"]
    gw_time = time_ctx["gw_time"]
    ns_time = time_ctx["ns_time"]
    received_at = time_ctx["received_at"]
    

    dr = radio.next_dr()
    sf = dr_to_sf(dr)

    metric = source["device_type"]
    weight = 0.0

    in_prod = _in_production_time(now_kst)

    # === production 시작 감지 ===
    if in_prod and not state["was_in_production"]:
        # 하루 새 사이클 시작
        state["last_event_time"] = None

    state["was_in_production"] = in_prod

    # =========================
    # UNIT_SCALE (1pc)
    # =========================
    if metric == "UNIT_SCALE":
        if in_prod:
            if random.random() < 0.025:
                if random.random() < 0.5:
                    weight = round(random.uniform(12.0, 12.8), 2)
                else:
                    weight = round(random.uniform(15.2, 16.0), 2)
            else:
                weight = round(random.uniform(13.0, 15.0), 2)
        else:
            weight = 0.0

    # =========================
    # PACK_SCALE (완제품 통)
    # =========================
    elif metric == "PACK_SCALE":
        if in_prod:
            last = state["last_event_time"]
            if last is None or (now_kst - last).total_seconds() >= 90:
                weight = round(random.uniform(125.0, 135.0), 1)
                state["last_event_time"] = now_kst
            else:
                weight = 0.0
        else:
            weight = 0.0

    # =========================
    # DOUGH_SCALE (반죽)
    # =========================
    elif metric == "DOUGH_SCALE":
        if in_prod:
            last = state["last_event_time"]
            if last is None or (now_kst - last).total_seconds() >= 900:
                weight = round(random.uniform(9800, 10200), 1)
                state["last_event_time"] = now_kst
            else:
                weight = 0.0
        else:
            weight = 0.0


    else:
        return None, None

    payload = {
        "deduplicationId": str(uuid.uuid4()),
        "time": time,
        "deviceInfo": {
            "tenantName": source["tenant_id"],
            "applicationName": "EF-Scale",
            "deviceProfileName": source["device_type"],
            "deviceName": source["device_name"],
            "devEui": radio.dev_eui,
        },
        "adr": True,
        "dr": dr,
        "fCnt": radio.next_fcnt(),
        "fPort": 8,
        "confirmed": False,
        "rxInfo": [
            {
                "gatewayId": "gw-ef-01",
                "gwTime": gw_time,
                "nsTime": ns_time,
                "rssi": radio.next_rssi(),
                "snr": radio.next_snr(),
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
        "values": {
            "weight": weight
        }
    }

    return payload, received_at
