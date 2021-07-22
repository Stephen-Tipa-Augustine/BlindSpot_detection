from mpu6050 import mpu6050
import time


class Accelerometer:

	def __init__(self, **kwargs):
		self.sensor = mpu6050(0x68)
		self.running = True

	def get_accelerometer_data(self):
		return self.sensor.get_accel_data()

	def get_gyroscope_data(self):
		return self.sensor.get_gyro_data()

	def get_temperature(self):
		return self.sensor.get_temp()

	def get_all_data(self):
		return self.sensor.get_all_data()

	def run(self):
		while self.running:
			print(self.get_accelerometer_data())
			time.sleep(5)

	def stop(self):
		self.running = False


if __name__ == "__main__":
	obj = Accelerometer()
	obj.run()
