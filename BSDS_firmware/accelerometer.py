from mpu6050 import mpu6050
import time


class Accelerometer:

    def __init__(self, **kwargs):
        self.sensor = None
        self.accel_data = None
        self.gyro_data = None
        self.running = True
        self.moving = False
        self.rotating = False
        self.initialize()
        
    def initialize(self, *args):
        try:
            self.sensor = mpu6050(0x68)
            self.accel_data = self.get_accelerometer_data()
            self.gyro_data = self.get_gyroscope_data()
            return False
        except:
            print('Failed to access the Accelerometer!')

    def get_accelerometer_data(self):
        try:
            return self.sensor.get_accel_data()
        except OSError as e:
            print('Loose connections to the accelerometer')
            return None

    def get_gyroscope_data(self):
        try:
            return self.sensor.get_gyro_data()
        except OSError as e:
            print('Loose connections to the accelerometer')
            return None

    def get_temperature(self):
        try:
            return self.sensor.get_temp()
        except OSError as e:
            print('Loose connections to the accelerometer')
            return None

    def get_all_data(self):
        try:
            return self.sensor.get_all_data()
        except OSError as e:
            print('Loose connections to the accelerometer')
            return None

    def detect_state(self, data, state_kind='accel'):
        accel_data  = self.get_accelerometer_data()
        gyro_data = self.get_gyroscope_data()
        if not self.sensor or not accel_data or not gyro_data or not data:
            return False
        current_values = accel_data if state_kind == 'accel' else gyro_data
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
