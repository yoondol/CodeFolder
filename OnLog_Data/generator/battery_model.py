# generator/battery_model.py

import random

class BatteryState:
    """
    8개월 ≈ 240일 ≈ 20,736,000초
    10초 주기 → 약 2,073,600 samples
    3000 → 2520 (480 감소)
    """
    DROP_PER_STEP = 480 / 2_073_600  # ≈ 0.00023

    def __init__(self):
        self.voltage = random.uniform(2900, 3000)

    def next(self):
        self.voltage -= self.DROP_PER_STEP
        if self.voltage <= 2520:
                    self.voltage = random.uniform(2900, 3000)
        return int(self.voltage)

    def status(self):
        if self.voltage < 2600:
            return 0b01  # Low
        elif self.voltage < 2800:
            return 0b10  # OK
        else:
            return 0b11  # Good
