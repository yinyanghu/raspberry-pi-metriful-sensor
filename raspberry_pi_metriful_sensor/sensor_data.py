class SensorData:
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def __str__(self):
        return "{} {}".format(self.value, self.unit)

    def get_value(self):
        return self.value

    def get_unit(self):
        return self.unit


class Temperature(SensorData):
    def __init__(self, value):
        super().__init__(value, "°C")


class Humidity(SensorData):
    def __init__(self, value):
        super().__init__(value, "%")


class Pressure(SensorData):
    def __init__(self, value):
        super().__init__(float(value) / 1000.0, "kPa")


t = Temperature(10)
print(t)
