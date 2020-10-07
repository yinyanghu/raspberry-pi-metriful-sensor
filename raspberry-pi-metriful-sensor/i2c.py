from time import sleep

import RPi.GPIO as GPIO
import smbus
from constant import *

I2C_BUS_NUMBER = 1
WAIT_INIT = 0.05
DEFAULT_LIGHT_INT_PIN = 7
DEFAULT_SOUND_INT_PIN = 8
DEFAULT_READY_PIN = 11


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

    def get_air_data(self):
        raw_data = self.i2c_bus.read_i2c_block_data(
            I2C_ADDR_7BIT_SB_OPEN, AIR_DATA_READ, AIR_DATA_BYTES)
        if (len(raw_data) != AIR_DATA_BYTES):
            raise Exception("Error on received air data")

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


m = MetrifulMS430(DEFAULT_LIGHT_INT_PIN,
                  DEFAULT_SOUND_INT_PIN, DEFAULT_READY_PIN)
