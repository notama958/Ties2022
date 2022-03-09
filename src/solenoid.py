import wiringpi
from time import sleep
gpio = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_GPIO)
solenoidpin = 18
gpio.pinMode(solenoidpin, gpio.OUTPUT)
wiringpi.pinMode(solenoidpin, 1)

while True:

    gpio.digitalWrite(solenoidpin, gpio.HIGH)
    sleep(0.06)
    gpio.digitalWrite(solenoidpin, gpio.LOW)

    sleep(0.1)

    gpio.digitalWrite(solenoidpin, gpio.HIGH)
    sleep(0.05)
    gpio.digitalWrite(solenoidpin, gpio.LOW)
