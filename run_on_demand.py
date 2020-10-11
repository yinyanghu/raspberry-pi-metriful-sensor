import RPi.GPIO as GPIO
from time import sleep
from raspberry_pi_metriful_sensor import MetrifulMS430


def main():
    m = MetrifulMS430()
    m.setup_particle_sensor()
    sleep(4)
    m.on_demand_measure_mode()

    m.detect_and_wait()
    print(m.get_air_data())
    print(m.get_light_data())
    print(m.get_sound_data())
    print(m.get_particle_data())

    GPIO.cleanup()


if __name__ == "__main__":
    main()
