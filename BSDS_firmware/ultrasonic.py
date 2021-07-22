# Libraries
import RPi.GPIO as GPIO
import time


class UltrasonicSensor:

    def __init__(self, **kwargs):
        # GPIO Mode (BOARD / BCM)
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
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back

        return "%.1f" % ((t * 34300) / 2)

    @staticmethod
    def clean_up(self):
        GPIO.cleanup()

    def run(self):
        while self.running:
            print("Measured Distance = %f cm" % self.compute_distance())
            time.sleep(1)

    def stop(self):
        self.running = False
        self.clean_up()


if __name__ == '__main__':
    obj = UltrasonicSensor()
    obj.run()
