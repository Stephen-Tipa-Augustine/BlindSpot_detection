from mpu6050 import mpu6050
import time
import threading


class Accelerometer:

    def __init__(self, **kwargs):
        self.sensor = mpu6050(0x68)
        self.running = True
        self.accel_data = self.get_accelerometer_data()
        self.gyro_data = self.get_gyroscope_data()
        self.moving = False
        self.rotating = False
        threading.Thread(target=self.run()).start()

    def get_accelerometer_data(self):
        return self.sensor.get_accel_data()

    def get_gyroscope_data(self):
        return self.sensor.get_gyro_data()

    def get_temperature(self):
        return self.sensor.get_temp()

    def get_all_data(self):
        return self.sensor.get_all_data()

    def detect_state(self, data, state_kind='accel'):
        current_values = self.get_accelerometer_data() if state_kind == 'accel' else self.get_gyroscope_data()
        difference = {'x': abs(current_values['x'] - data['x']),
                      'y': abs(current_values['y'] - data['y']),
                      'z': abs(current_values['z'] - data['z'])}
        changed_axis = 0
        for i in difference:
            if difference[i] > 2:
                changed_axis += 1
        return False if current_values <= 1 else True

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
