from .ultrasonic import UltrasonicSensor
from kivy.clock import Clock
import time
from .helpers import ThreadManager
import threading

# Constants
REFERENCE_DISTANCE = 100  # in centimeter
MAXIMUM_DISTANCE = 450  # theoretical, angle < 15 degrees
DRIFT = 30


class DistantManager:

    def __init__(self):
        self.left_sensor = None
        self.rear_sensor = None
        self.right_sensor = None
        self.front_sensor = None
        self.raw_rear_data = []
        self.left_sensor_value = None
        self.rear_sensor_value = None
        self.right_sensor_value = None
        self.front_sensor_value = None

        self.initialize_sensors()

    def initialize_sensors(self):
        self.rear_sensor = UltrasonicSensor()

    def read_left_sensor(self):
        return self.rear_sensor.run()

    def read_rear_sensor(self):
        pass

    def read_right_sensor(self):
        pass

    def read_front_sensor(self):
        pass

    def run(self, q=None):
        while True:
            result = self.read_left_sensor()
            if q:
                q.put(
                    {'left': (result, 'in' if result < REFERENCE_DISTANCE else 'out') if result else None,
                     'bottom': None,
                     'right': None, 'top': None}
                )
