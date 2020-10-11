from enum import Enum
from time import sleep

import RPi.GPIO as GPIO
import smbus
from .code import *

I2C_ADDR = I2C_ADDR_7BIT_SB_OPEN
I2C_BUS_NUMBER = 1
WAIT_READY = 0.05
WAIT_RESET = 0.005
RAW_DATA_CATEGORY = {
    "air": (AIR_DATA_READ, AIR_DATA_BYTES),
    "air_quality": (AIR_QUALITY_DATA_READ, AIR_QUALITY_DATA_BYTES),
    "light": (LIGHT_DATA_READ, LIGHT_DATA_BYTES),
    "sound": (SOUND_DATA_READ, SOUND_DATA_BYTES),
    "particle": (PARTICLE_DATA_READ, PARTICLE_DATA_BYTES),
}
CYCLE_PERIOD = {
    "3s": CYCLE_PERIOD_3_S,
    "100s": CYCLE_PERIOD_100_S,
    "300s": CYCLE_PERIOD_300_S,
}
DEFAULT_LIGHT_INT_PIN = 7
DEFAULT_SOUND_INT_PIN = 8
DEFAULT_READY_PIN = 11


class Mode(Enum):
    STANDBY = 0
    ON_DEMAND = 1
    CYCLE = 2


class MetrifulMS430:
    def __init__(self,
                 light_int_pin=DEFAULT_LIGHT_INT_PIN,
                 sound_int_pin=DEFAULT_SOUND_INT_PIN,
                 ready_pin=DEFAULT_READY_PIN):
        self.light_int_in = light_int_pin
        self.sound_int_pin = sound_int_pin
        self.ready_pin = ready_pin
        self.mode = Mode.STANDBY
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(ready_pin, GPIO.IN)
        GPIO.setup(light_int_pin, GPIO.IN)
        GPIO.setup(sound_int_pin, GPIO.IN)

        self.i2c_bus = smbus.SMBus(I2C_BUS_NUMBER)
        self.wait_ready()

        self.reset()
        GPIO.add_event_detect(ready_pin, GPIO.FALLING)

    def reset(self):
        self.i2c_bus.write_byte(I2C_ADDR, RESET_CMD)
        sleep(WAIT_RESET)
        self.wait_ready()

    def setup_particle_sensor(self):
        self.i2c_bus.write_i2c_block_data(
            I2C_ADDR, PARTICLE_SENSOR_SELECT_REG, [PARTICLE_SENSOR_PPD42])

    def on_demand_measure_mode(self):
        self.i2c_bus.write_byte(I2C_ADDR, ON_DEMAND_MEASURE_CMD)
        self.mode = Mode.ON_DEMAND

    def cycle_mode(self, cycle="3s"):
        self.i2c_bus.write_i2c_block_data(
            I2C_ADDR, CYCLE_TIME_PERIOD_REG, [CYCLE_PERIOD[cycle]])
        self.i2c_bus.write_byte(I2C_ADDR, CYCLE_MODE_CMD)
        self.mode = Mode.CYCLE

    def wait_ready(self):
        while GPIO.input(self.ready_pin) == 1:
            sleep(WAIT_READY)

    def detect_and_wait(self):
        while not GPIO.event_detected(self.ready_pin):
            sleep(WAIT_READY)

    def get_raw_data(self, key):
        category, data_bytes = RAW_DATA_CATEGORY[key]
        raw_data = self.i2c_bus.read_i2c_block_data(
            I2C_ADDR, category, data_bytes)
        if (len(raw_data) != data_bytes):
            raise Exception("Error on received data")
        return raw_data

    def get_air_data(self):
        raw_data = self.get_raw_data("air")
        return {
            "temperature": self.get_temperature(raw_data),
            "pressure": self.get_pressure(raw_data),
            "humidity": self.get_humidity(raw_data),
            "gas_sensor_resistance": self.get_gas_sensor_resistance(raw_data),
        }

    def get_air_quality_data(self):
        if self.mode != Mode.CYCLE:
            raise Exception(
                "Not support air quality data in {} mode".format(self.mode.name))
        raw_data = self.get_raw_data("air_quality")
        return {
            "aqi": self.get_aqi(raw_data),
            "aqi_accuracy": self.get_aqi_accuracy(raw_data),
            "co2": self.get_co2(raw_data),
            "b_voc": self.get_b_voc(raw_data),
        }

    def get_light_data(self):
        raw_data = self.get_raw_data("light")
        return {
            "illumination'": self.get_illumination(raw_data),
            "white": self.get_white(raw_data),
        }

    def get_sound_data(self):
        raw_data = self.get_raw_data("sound")
        return {
            "spl": self.get_spl(raw_data),
            "spl_bands": self.get_spl_bands(raw_data),
            "peak_amp": self.get_peak_amp(raw_data),
            "stable": self.get_stable(raw_data),
        }

    def get_particle_data(self):
        raw_data = self.get_raw_data("particle")
        return {
            "duty_cycle_pc": self.get_duty_cycle_pc(raw_data),
            "concentration": self.get_concentration(raw_data),
            "valid": self.get_valid(raw_data),
        }

    def get_duty_cycle_pc(self, raw_data):
        return raw_data[0] + float(raw_data[1]) / 100.0

    def get_concentration(self, raw_data):
        return raw_data[2] + (raw_data[3] << 8) + float(raw_data[4]) / 100.0

    def get_valid(self, raw_data):
        return raw_data[5] > 0

    def get_spl(self, raw_data):
        return raw_data[0] + float(raw_data[1]) / 10.0

    def get_spl_bands(self, raw_data):
        sql_bands = []
        for i in range(SOUND_FREQ_BANDS):
            s = raw_data[2 + i] + \
                float(raw_data[2 + i + SOUND_FREQ_BANDS]) / 10.0
            sql_bands.append(s)
        return sql_bands

    def get_peak_amp(self, raw_data):
        i = 2 + 2 * SOUND_FREQ_BANDS
        return raw_data[i] + (raw_data[i + 1] << 8) + float(raw_data[i + 2]) / 100.0

    def get_stable(self, raw_data):
        return raw_data[5 + 2 * SOUND_FREQ_BANDS]

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

    def get_illumination(self, raw_data):
        return raw_data[0] + (raw_data[1] << 8) + float(raw_data[2]) / 100.0

    def get_white(self, raw_data):
        return raw_data[3] + (raw_data[4] << 8)
