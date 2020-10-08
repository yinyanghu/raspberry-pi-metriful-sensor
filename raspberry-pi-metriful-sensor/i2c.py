from time import sleep

import RPi.GPIO as GPIO
import smbus
from constant import *

I2C_BUS_NUMBER = 1
WAIT_INIT = 0.05
DEFAULT_LIGHT_INT_PIN = 7
DEFAULT_SOUND_INT_PIN = 8
DEFAULT_READY_PIN = 11
RAW_DATA_CATEGORY = {
    "air": (AIR_DATA_READ, AIR_DATA_BYTES),
    "air_quality": (AIR_QUALITY_READ, AIR_QUALITY_DATA_BYTES),
}


class MetrifulMS430:
    def __init__(self, light_int_pin, sound_int_pin, ready_pin):
        self.light_int_in = light_int_pin
        self.sound_int_pin = sound_int_pin
        self.ready_pin = ready_pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(ready_pin, GPIO.IN)
        GPIO.setup(light_int_pin, GPIO.IN)
        GPIO.setup(sound_int_pin, GPIO.IN)

        self.i2c_bus = smbus.SMBus(I2C_BUS_NUMBER)
        self.init_and_wait()
        self.i2c_bus.write_byte(I2C_ADDR_7BIT_SB_OPEN, RESET_CMD)
        self.init_and_wait()
        GPIO.add_event_detect(ready_pin, GPIO.FALLING)

    def init_and_wait(self):
        while (GPIO.input(self.ready_pin) == 1):
            sleep(WAIT_INIT)

    def get_raw_data(self, key):
        category, data_bytes = RAW_DATA_CATEGORY[key]
        raw_data = self.i2c_bus.read_i2c_block_data(
            I2C_ADDR_7BIT_SB_OPEN, category, data_bytes)
        if (len(raw_data) != data_bytes):
            raise Exception("Error on received data")
        return raw_data

    def get_air_data(self):
        raw_data = self.get_raw_data("air")
        return {
            "temperature": self.get_temperature(raw_data),
            "pressure": self.get_pressure(raw_data),
            "humidity": self.get_humidity(raw_data),
            "gas_sensor_resistance": self.gas_sensor_resistance(raw_data),
        }

    def get_air_quality_data(self):
        raw_data = self.get_raw_data("air_quality")
        return {
            "aqi": self.get_aqi(raw_data),
            "aqi_accuracy": self.get_aqi_accuracy(raw_data),
            "co2": self.get_co2(raw_data),
            "b_voc": self.get_b_voc(raw_data),
        }

    def get_temperature(self, raw_data):
        t = (raw_data[0] & TEMPERATURE_VALUE_MASK) + \
            (float(raw_data[1]) / 10.0)
        return t if (raw_data[0] & TEMPERATURE_SIGN_MASK) == 0 else -t

    def get_pressure(self, raw_data):
        return (raw_data[5] << 24) + (raw_data[4] << 16) + (raw_data[3] << 8) + raw_data[2]

    def get_humidity(self, raw_data):
        return raw_data[6] + float(raw_data[7]) / 10.0

    def get_gas_sensor_resistance(self, raw_data):
        return (raw_data[11] << 24) + (raw_data[10] << 16) + (raw_data[9] << 8) + raw_data[8]

    def get_aqi(self, raw_data):
        return raw_data[0] + (raw_data[1] << 8) + float(raw_data[2]) / 10.0

    def get_co2(self, raw_data):
        return raw_data[3] + (raw_data[4] << 8) + float(raw_data[5]) / 10.0

    def get_b_voc(self, raw_data):
        return raw_data[6] + (raw_data[7] << 8) + float(raw_data[8]) / 10.0

    def get_aqi_accuracy(self, raw_data):
        return raw_data[9]


m = MetrifulMS430(DEFAULT_LIGHT_INT_PIN,
                  DEFAULT_SOUND_INT_PIN, DEFAULT_READY_PIN)
