class Bus:
    def __init__(self, number=9999):
        self.number = number
        self.fuel = 0.0
        self.dest = None
        print(f"No {self.number}: Prepared")

    def get_status(self):
        dest_status = self.dest if self.dest else "No Dest"
        return f"No {self.number}: {self.fuel:.1f} Liter(s), {dest_status}"

    def add_fuel(self, amount):
        self.fuel += amount
        print(f"No {self.number}: Fuel {self.fuel:.1f} Liter(s)")

    def move(self):
        if not self.dest:
            print(f"No {self.number}: No Dest")
        elif self.fuel == 0:
            print(f"No {self.number}: No Fuel")
        else:
            self.fuel /= 2
            print(f"No {self.number}: Move to {self.dest}")

    def __str__(self):
        dest_status = self.dest if self.dest else "No Dest"
        return f"No {self.number}: {self.fuel:.1f} Liter(s), {dest_status}"


a1 = Bus(1234)
b1 = Bus()
print(a1.get_status())
print(b1.get_status())
a1.add_fuel(10)
a1.dest = 'Busan'
a1.move()
b1.move()
b1.dest = 'Daegu'
b1.move()
print(a1)
print(b1)