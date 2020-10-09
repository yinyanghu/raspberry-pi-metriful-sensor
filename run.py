import RPi.GPIO as GPIO
from raspberry_pi_metriful_sensor import MetrifulMS430

DEFAULT_LIGHT_INT_PIN = 7
DEFAULT_SOUND_INT_PIN = 8
DEFAULT_READY_PIN = 11

m = MetrifulMS430(DEFAULT_LIGHT_INT_PIN,
                  DEFAULT_SOUND_INT_PIN, DEFAULT_READY_PIN)
m.setup_particle_sensor()
m.on_demand_measure_mode()
m.detect_and_wait()
print(m.get_air_data())
print(m.get_light_data())
print(m.get_sound_data())
print(m.get_particle_data())

GPIO.cleanup()
