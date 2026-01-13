# generator/battery_model.py

class BatteryState:
    def __init__(self):
        self.voltage = 3000

    def next(self):
        self.voltage -= 1
        if self.voltage <= 2520:
            self.voltage = 3000
        return self.voltage

    def status(self):
        if self.voltage < 2600:
            return 0b01
        elif self.voltage < 2800:
            return 0b10
        else:
            return 0b11
