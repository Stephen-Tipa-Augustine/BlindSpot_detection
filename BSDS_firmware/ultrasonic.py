# Libraries
import threading

import RPi.GPIO as GPIO
import time
from .helpers import ThreadManager


class UltrasonicSensor:

    def __init__(self, **kwargs):
        # GPIO Mode (BOARD / BCM)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # set GPIO Pins
        self.GPIO_TRIGGER = 18
        self.GPIO_ECHO = 24
        # set GPIO direction (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)

        self.running = True

    def compute_distance(self):
        # set Trigger to HIGH
        GPIO.output(self.GPIO_TRIGGER, True)
        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.GPIO_TRIGGER, False)
        start_time = time.time()
        stop_time = time.time()
        # save StartTime
        while GPIO.input(self.GPIO_ECHO) == 0:
            start_time = time.time()
        # save time of arrival
        while GPIO.input(self.GPIO_ECHO) == 1:
            stop_time = time.time()
        # time difference between start and arrival
        t = stop_time - start_time
        return float("%.1f" % ((t * 34300) / 2))

    @staticmethod
    def clean_up():
        GPIO.cleanup()

    def run(self):
        return self.compute_distance()

    def stop(self):
        self.running = False
        self.clean_up()


if __name__ == '__main__':
    obj = UltrasonicSensor()
    obj.run()
