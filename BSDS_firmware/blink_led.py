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
        self.running = True

    def turn_off(self):
        GPIO.output(self.GPIO_LED, GPIO.LOW)
        time.sleep(1)

    def turn_on(self):
        GPIO.output(self.GPIO_LED, GPIO.HIGH)
        time.sleep(1)

    @staticmethod
    def clean_up(self):
        GPIO.cleanup()

    def run(self):
        while self.running:
            self.turn_on()
            self.turn_off()

    def stop(self):
        self.running = False
        self.turn_off()
        self.clean_up()


if __name__ == '__main__':
    obj = BlinkLED()
    obj.run()
