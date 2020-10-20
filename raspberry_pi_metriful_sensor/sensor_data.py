import math


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


class Percent(SensorData):
    def __init__(self, percent):
        super().__init__(value, "%")


class Index(SensorData):
    def __init__(self, index):
        super().__init__(index, None)


class Temperature(SensorData):
    def __init__(self, value):
        super().__init__(value, "°C")


class Humidity(Percent):
    def __init__(self, value):
        super().__init__(value)


class Pressure(SensorData):
    def __init__(self, value):
        super().__init__(float(value) / 1000.0, "kPa")


class AirQualityAccuracy(Index):
    LEVEL = {
        0: "not available",
        1: "low",
        2: "medium",
        3: "high",
    }
    STATUS = {
        0: "calibration incomplete",
        1: "calibration ongoing",
        2: "calibration ongoing",
        3: "calibration done",
    }

    def __init__(self, index):
        super().__init__(index)

    def __str__(self):
        return "{}, {}".format(self.LEVEL[self.value], self.STATUS[self.value])


class AirQualityIndex(Index):
    RANGE = {
        (0, 50): "good",
        (51, 100): "acceptable",
        (101, 150): "substandard",
        (151, 200): "poor",
        (201, 300): "bad",
        (301, 500): "very bad",
        (500, math.inf): "oh my god",
    }

    def __init__(self, index, accuracy):
        super().__init__(index)
        self.accuracy = AirQualityAccuracy(accuracy)

    def __str__(self):
        return "{}: {} (accuracy: {})".format(
            self.value, self.eval(), str(self.accuracy))

    def eval(self):
        for (l, r), v in self.RANGE.items():
            if self.value >= l and self.value <= r:
                return v


class CO2(SensorData):
    def __init__(self, value):
        super().__init__(value, "PPM")


class BreathVOC(SensorData):
    def __init__(self, value):
        super().__init__(value, "PPM")


print(Temperature(10))
print(AirQualityIndex(25, 2))
print(AirQualityIndex(125, 0))
print(AirQualityIndex(200, 1))
print(AirQualityIndex(250, 2))
print(AirQualityIndex(400, 2))
print(AirQualityIndex(700, 3))
