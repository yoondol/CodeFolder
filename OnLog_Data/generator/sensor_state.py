# generator/sensor_state.py

import random
import uuid

class SensorState:
    def __init__(self, key):
        self.key = key

        # 고유 식별자
        self.dev_eui = uuid.uuid4().hex[:16]

        # DR 거의 고정
        self.dr = random.choice([0, 1, 2, 3, 4, 5])

        # RSSI 그룹: 강 / 약
        if random.random() < 0.5:
            self.rssi_base = random.randint(-70, -60)
        else:
            self.rssi_base = random.randint(-120, -110)

        # SNR 기준값
        self.snr_base = random.uniform(-5.0, 5.0)

        # Frame counter
        self.fcnt = random.randint(0, 1000)

    def next_dr(self):
        # 아주 가끔만 DR 변경
        if random.random() < 0.001:
            self.dr = random.choice([0, 1, 2, 3, 4, 5])
        return self.dr

    def next_rssi(self):
        return self.rssi_base + random.randint(-1, 1)

    def next_snr(self):
        return round(self.snr_base + random.uniform(-1.0, 1.0), 2)

    def next_fcnt(self):
        self.fcnt += 1
        return self.fcnt
