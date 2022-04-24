#!/usr/bin/env python3
# File name   : servo.py
# Description : Control lights
# Author	  : William
# Date		: 2019/02/23
import time
import RPi.GPIO as GPIO
import sys
import os
from rpi_ws281x import *
import threading

# curr_folder = os.path.dirname(os.getcwd())
# sys.path.append(curr_folder)
# from navigation import compass_smbus_cmps14
BLUE = 0
GREEN = 1
RED = 2
WHITE = 3
RGB_CODES = [
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (255, 255, 255),
]


class RobotLight(threading.Thread):
    def __init__(self, *args, **kwargs):
        # compass=compass_smbus_cmps14.Compass(4)
        # compass.start()
        self.LED_COUNT = 12	  # Number of LED pixels.
        self.LED_PIN = 12	  # GPIO pin connected to the pixels (18 uses PWM!).
        # LED signal frequency in hertz (usually 800khz)
        self.LED_FREQ_HZ = 800000
        self.LED_DMA = 10	  # DMA channel to use for generating signal (try 10)
        self.LED_BRIGHTNESS = 255	 # Set to 0 for darkest and 255 for brightest
        # True to invert the signal (when using NPN transistor level shift)
        self.LED_INVERT = False
        self.LED_CHANNEL = 0	   # set to '1' for GPIOs 13, 19, 41, 45 or 53

        self.colorBreathR = 255
        self.colorBreathG = 255
        self.colorBreathB = 255
        self.breathSteps = 10

        self.lightMode = 'breath'  # 'none' 'police' 'breath'

        self.port = 1

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(5, GPIO.OUT)
        GPIO.setup(6, GPIO.OUT)
        GPIO.setup(13, GPIO.OUT)

        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ,
                                       self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()

        super(RobotLight, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()
        self.resume()

    def setOneLED(self, rgb_color, index):
        if index in range(self.LED_COUNT):
            self.strip.setPixelColor(index, rgb_color)

    # Define functions which animate LEDs in various ways.
    def setColor(self, R, G, B):
        """Wipe color across display a pixel at a time."""
        color = Color(int(R), int(G), int(B))
        for i in range(self.strip.numPixels()):
            self.setOneLED(color, i)
        self.strip.show()

    def setSomeColor(self, color_code):
        (R, G, B) = RGB_CODES[color_code]
        color = Color(int(R), int(G), int(B))
        #print(int(R),'  ',int(G),'  ',int(B))
        for i in range(0, self.LED_COUNT):
            self.setOneLED(color, i)
        self.strip.show()

    def pause(self):
        self.lightMode = 'none'
        self.setColor(0, 0, 0)
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def police(self):
        self.lightMode = 'police'
        self.resume()

    def policeProcessing(self):
        while self.lightMode == 'police':
            for i in range(0, 3):
                self.setSomeColor(
                    BLUE)
                time.sleep(0.05)
                self.setSomeColor(
                    WHITE)
                time.sleep(0.05)
            if self.lightMode != 'police':
                break
            time.sleep(0.1)
            for i in range(0, 3):
                self.setSomeColor(
                    RED)
                time.sleep(0.05)
                self.setSomeColor(
                    WHITE)
                time.sleep(0.05)
            time.sleep(0.1)

    def breath(self, color_code):
        self.lightMode = 'breath'
        self.colorBreathR, self.colorBreathG, self.colorBreathB = RGB_CODES[color_code]
        self.resume()

    def breathProcessing(self):
        while self.lightMode == 'breath':
            for i in range(0, self.breathSteps):
                if self.lightMode != 'breath':
                    break
                self.setColor(self.colorBreathR*i/self.breathSteps, self.colorBreathG *
                              i/self.breathSteps, self.colorBreathB*i/self.breathSteps)
                time.sleep(0.1)
            for i in range(0, self.breathSteps):
                if self.lightMode != 'breath':
                    break
                self.setColor(self.colorBreathR-(self.colorBreathR*i/self.breathSteps), self.colorBreathG-(
                    self.colorBreathG*i/self.breathSteps), self.colorBreathB-(self.colorBreathB*i/self.breathSteps))
                time.sleep(0.1)

    def frontLight(self, switch):
        if switch == 'on':
            GPIO.output(6, GPIO.HIGH)
            GPIO.output(13, GPIO.HIGH)
        elif switch == 'off':
            GPIO.output(5, GPIO.LOW)
            GPIO.output(13, GPIO.LOW)

    def blink(self, port):
        """hat led control"""
        self.switch(port, 0)
        time.sleep(0.5)
        self.switch(port, 1)
        time.sleep(0.5)

    def switch(self, port, status):
        if port == 1:
            if status == 1:
                GPIO.output(5, GPIO.HIGH)
            elif status == 0:
                GPIO.output(5, GPIO.LOW)
            else:
                pass
        elif port == 2:
            if status == 1:
                GPIO.output(6, GPIO.HIGH)
            elif status == 0:
                GPIO.output(6, GPIO.LOW)
            else:
                pass
        elif port == 3:
            if status == 1:
                GPIO.output(13, GPIO.HIGH)
            elif status == 0:
                GPIO.output(13, GPIO.LOW)
            else:
                pass
        else:
            print('Wrong Command: Example--switch(3, 1)->to switch on port3')

    def set_all_switch_off(self):
        self.switch(1, 0)
        self.switch(2, 0)
        self.switch(3, 0)

    def headLight(self, switch):
        if switch == 'on':
            GPIO.output(5, GPIO.HIGH)
        elif switch == 'off':
            GPIO.output(5, GPIO.LOW)

    def wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        # return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)
        return (r, g, b)

    def rainbow_cycle(self, wait):
        self.lightMode = 'rainbow'
        self.rainbowProcessing(wait)

    def rainbowProcessing(self, wait):
        while self.lightMode == 'rainbow':
            for j in range(255):
                for i in range(self.LED_COUNT):
                    pixel_index = (i * 256 // self.LED_COUNT) + j
                    R, G, B = self.wheel(pos=pixel_index & 255)
                    color = Color(int(R), int(G), int(B))
                    self.strip.setPixelColor(i, color)
                self.strip.show()
                time.sleep(wait)

    def wave_cycle(self, wait):
        """"""

    def setMode(self, mode):
        """set light mode"""
        self.lightMode = mode

    def lightChange(self):
        if self.lightMode == 'none':
            self.pause()
        elif self.lightMode == 'police':
            self.policeProcessing()
        elif self.lightMode == 'breath':
            self.breathProcessing()
        elif self.lightMode == 'rainbow':
            self.rainbowProcessing(0.01)

    def run(self):
        while 1:
            self.__flag.wait()
            self.lightChange()
            print('hihi')
            pass


if __name__ == '__main__':
    RL = RobotLight()
    RL.start()
    # while 1:
    #     RL.rainbow_cycle(0.001)
    # RL.setMode('breath')
    RL.breath(BLUE)
    time.sleep(1)
    # RL.rainbow_cycle(0.01)
    time.sleep(1)
    RL.breath(WHITE)
    # time.sleep(15)
    # RL.pause()
    # RL.frontLight('off')
    # time.sleep(2)
    # RL.police()
    # time.sleep(2)
