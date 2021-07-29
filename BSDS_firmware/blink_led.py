# Libraries
import RPi.GPIO as GPIO
import time


class BlinkLED:

    def __init__(self, **kwargs):
        # GPIO Mode (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # set GPIO Pins
        self.GPIO_LED = 25

        # set GPIO direction (IN / OUT)
        GPIO.setup(self.GPIO_LED, GPIO.OUT)

    def turn_off(self, delay=1.):
        GPIO.output(self.GPIO_LED, GPIO.LOW)
        time.sleep(delay)

    def turn_on(self, delay=1.):
        GPIO.output(self.GPIO_LED, GPIO.HIGH)
        time.sleep(delay)

    @staticmethod
    def clean_up():
        GPIO.cleanup()

    def run(self, delay=2):
        self.turn_on(delay=delay * .4)
        self.turn_off(delay=delay * .4)

    def stop(self):
        self.turn_off()
        self.clean_up()


if __name__ == '__main__':
    obj = BlinkLED()
    obj.run()
