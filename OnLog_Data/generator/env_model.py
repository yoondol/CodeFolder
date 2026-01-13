# generator/env_model.py

import math
import random
from datetime import datetime

################################
# 계절 기준 테이블 (월 → mean/range/drift)
################################
SEASON_PROFILE = {
    1:  (4,  4, 35, 12, 0.03),
    2:  (7,  5, 40, 14, 0.05),
    3:  (11, 7, 48, 18, 0.10),
    4:  (17, 9, 55, 22, 0.14),
    5:  (23, 11, 58, 28, 0.10),
    6:  (27, 12, 68, 35, 0.05),
    7:  (30, 8, 78, 45, 0.02),
    8:  (28, 8, 75, 40, 0.02),
    9:  (24, 11, 55, 30, 0.12),
    10: (18, 9, 58, 25, 0.08),
    11: (11, 6, 65, 18, 0.04),
    12: (6,  4, 72, 12, 0.02),
}

################################
# 공간 그룹별 오프셋
################################
SPACE_PROFILE = {
    "WAREHOUSE":   ( +3, 0.6, +0, 0.7),
    "COOL":        ( -5, 0.4, +10, 0.4),
    "HEAT":        ( +8, 0.5, -20, 0.3),
    "DRY":         ( +6, 0.4, -30, 0.2),
    "INNER_PACK":  ( +1, 0.5,  -7, 0.4),
    "OUTER_PACK":  ( +1, 0.7,  +0, 0.7),
    "DOUGH":       ( +3, 0.6,  +7, 0.5),
    "ENTRANCE":    (  0, 1.2,  +0, 1.1),
}

################################
# 센서 그룹 매핑
################################
SENSOR_GROUP = {
    1: "COOL",
    2: "HEAT",
    3: "INNER_PACK",
    4: "WAREHOUSE",
    5: "DRY",
    6: "ENTRANCE",
    7: "WAREHOUSE",
    8: "DOUGH",
    9: "HEAT",
    10: "DRY",
    11: "WAREHOUSE",
    12: "OUTER_PACK",
}


def generate_env_value(sensor_no: int, now: datetime, prev=None):
    month = now.month
    hour = now.hour + now.minute / 60

    temp_mean, temp_range, hum_mean, hum_range, drift = SEASON_PROFILE[month]
    temp_off, temp_sens, hum_off, hum_sens = SPACE_PROFILE[SENSOR_GROUP[sensor_no]]

    # 일중 사인파 (최고 14시, 최저 6시)
    phase = (hour - 6) / 24 * 2 * math.pi
    diurnal = math.sin(phase)

    temp = temp_mean + temp_off \
           + diurnal * temp_range * temp_sens \
           + random.uniform(-0.3, 0.3)

    hum = hum_mean + hum_off \
          - diurnal * hum_range * hum_sens \
          + random.uniform(-2, 2)

    # day-to-day drift
    if prev:
        temp += (prev["temp"] - temp) * drift
        hum += (prev["hum"] - hum) * drift

    return round(temp, 2), round(max(5, min(95, hum)), 1)
