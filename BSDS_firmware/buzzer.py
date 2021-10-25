import RPi.GPIO as GPIO
from time import sleep
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

buzzer=26
GPIO.setup(buzzer, GPIO.OUT)

while True:
	GPIO.output(buzzer, GPIO.HIGH)
	print('Beep')
	sleep(.5)
	GPIO.output(buzzer, GPIO.LOW)
	print('No beep')
	sleep(.5)
