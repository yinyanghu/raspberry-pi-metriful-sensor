import signal
import sys

import RPi.GPIO as GPIO
from time import sleep
from raspberry_pi_metriful_sensor import MetrifulMS430

WAIT_INIT = 2


def sigint_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, sigint_handler)

    m = MetrifulMS430()
    m.setup_particle_sensor()
    m.cycle_mode()

    sleep(WAIT_INIT)

    while True:
        m.detect_and_wait()
        print(m.get_air_data())
        print(m.get_air_quality_data())
        print(m.get_light_data())
        print(m.get_sound_data())
        print(m.get_particle_data())
        print()


if __name__ == "__main__":
    main()
