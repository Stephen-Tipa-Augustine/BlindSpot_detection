# Libraries
import RPi.GPIO as GPIO
import time


class BlinkLED:

    def __init__(self, cathode, **kwargs):
        # GPIO Mode (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # set GPIO Pins
        self.GPIO_LED = cathode

        # set GPIO direction (IN / OUT)
        GPIO.setup(self.GPIO_LED, GPIO.OUT)
        self.state = False
        self.blinking = True

    def turn_off(self):
        GPIO.output(self.GPIO_LED, GPIO.LOW)
        self.state = False

    def turn_on(self):
        GPIO.output(self.GPIO_LED, GPIO.HIGH)
        self.state = True

    @staticmethod
    def clean_up():
        GPIO.cleanup()

    def run(self, turn_off=False):
        if self.state or turn_off:
            self.turn_off()
        else:
            self.turn_on()

    def stop(self):
        self.state = False
        self.blinking = False
        self.turn_off()
        self.clean_up()


if __name__ == '__main__':
    obj = BlinkLED()
    obj.run()
