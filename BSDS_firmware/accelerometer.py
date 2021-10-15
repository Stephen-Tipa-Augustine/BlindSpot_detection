from mpu6050 import mpu6050
import time
import threading
from kivy.clock import Clock


class Accelerometer:

    def __init__(self, **kwargs):
        self.sensor = None
        self.accel_data = None
        self.gyro_data = None
        Clock.schedule_interval(self.initialize, timeout=5)
        self.running = True
        self.moving = False
        self.rotating = False
        # threading.Thread(target=self.run()).start()
        
    def initialize(self, *args):
        try:
            self.sensor = mpu6050(0x68)
            self.accel_data = self.get_accelerometer_data()
            self.gyro_data = self.get_gyroscope_data()
            return False
        except:
            print('Failed to access the Accelerometer!')

    def get_accelerometer_data(self):
        return self.sensor.get_accel_data()

    def get_gyroscope_data(self):
        return self.sensor.get_gyro_data()

    def get_temperature(self):
        return self.sensor.get_temp()

    def get_all_data(self):
        return self.sensor.get_all_data()

    def detect_state(self, data, state_kind='accel'):
        if not self.sensor:
            return False
        current_values = self.get_accelerometer_data() if state_kind == 'accel' else self.get_gyroscope_data()
        difference = {'x': abs(current_values['x'] - data['x']),
                      'y': abs(current_values['y'] - data['y']),
                      'z': abs(current_values['z'] - data['z'])}
        changed_axis = 0
        for i in difference:
            if difference[i] > 2:
                changed_axis += 1
        return False if changed_axis < 1 else True

    def vehicle_moving(self):
        self.moving = self.detect_state(self.accel_data)
        self.accel_data = self.get_accelerometer_data()

    def vehicle_rotating(self):
        self.rotating = self.detect_state(self.gyro_data, state_kind='gyro')
        self.gyro_data = self.get_gyroscope_data()

    def run(self):
        while self.running:
            self.vehicle_moving()
            self.vehicle_rotating()
            time.sleep(5)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    obj = Accelerometer()
    obj.run()
