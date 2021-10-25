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
        self.left_sensor = UltrasonicSensor(trigger=18, echo=24)
        self.right_sensor = UltrasonicSensor(trigger=17, echo=27)

    def read_left_sensor(self):
        return self.left_sensor.run()

    def read_rear_sensor(self):
        pass

    def read_right_sensor(self):
        return self.right_sensor.run()

    def read_front_sensor(self):
        pass

    def run(self):
        # while True:
        m = ThreadManager()
        t1 = threading.Thread(target=lambda q: q.put(self.read_left_sensor()), args=(m.que,))
        t1.start()
        t2 = threading.Thread(target=lambda q: q.put(self.read_right_sensor()), args=(m.que,))
        t2.start()
        m.add_thread(t1)
        m.add_thread(t2)
        m.join_threads()
        left_result = m.check_for_return_value()
        right_result = m.check_for_return_value()
        return {'left': (left_result, 'in' if left_result < REFERENCE_DISTANCE else 'out') if left_result else None,
                'bottom': None,
                'right': (right_result, 'in' if right_result < REFERENCE_DISTANCE else 'out') if right_result else None,
                'top': None}
