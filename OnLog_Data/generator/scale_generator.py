# generator/scale_generator.py

import uuid
import json
import random
from sensor_state import SensorState
from time_utils import generate_times, dr_to_sf
from env_generator import FREQUENCIES, _get_state


def generate_scale_payload(source):
    state = _get_state(source)

    time, gw_time, ns_time, received_at = generate_times()

    dr = state.next_dr()
    sf = dr_to_sf(dr)

    if source["device_type"] == "UNIT_SCALE":
        weight = round(random.uniform(13.5, 14.5), 2)
    elif source["device_type"] == "DOUGH_SCALE":
        weight = round(random.uniform(980, 1020), 1)
    else:
        weight = round(random.uniform(4800, 5200), 1)

    payload = {
        "deduplicationId": str(uuid.uuid4()),
        "time": time,
        "deviceInfo": {
            "tenantName": source["tenant_id"],
            "applicationName": "EF-Scale",
            "deviceProfileName": source["device_type"],
            "deviceName": source["device_name"],
            "devEui": state.dev_eui,
        },
        "adr": True,
        "dr": dr,
        "fCnt": state.next_fcnt(),
        "fPort": 8,
        "confirmed": False,
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
        "values": {
            "weight": weight
        }
    }

    return payload, received_at
