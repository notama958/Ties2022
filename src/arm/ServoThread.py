# Servo thread for each servo pin
# author: Yen Tran

import busio
from board import SCL, SDA
import threading
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
import time


i2c = busio.I2C(SCL, SDA)


# https://circuitpython.readthedocs.io/projects/pca9685/en/latest/examples.html


pca = PCA9685(i2c)
pca.frequency = 50


class ServoThreadObject(threading.Thread):
    angle = 90  # init pos
    maxPos = 180
    minPos = 0
    scDelay = 0.3

    def __init__(self, servoObject, *args, **kwargs):
        self.servo = servoObject
        super(ServoThreadObject, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.set()

    def pause(self):
        print('......................pause..........................')
        self.__flag.clear()

    def resume(self):
        print('resume')
        self.__flag.set()

    def moveAngle(self, angle):
        """move servo to specific angle"""
        if self.angle != angle:
            self.angle = angle
            self.servo.angle = angle  # set new value to servo

    def killServoThread(self):
        self.__flag.clear()

    def run(self):
        while True:
            """"""
            # self.moveAngle()


if __name__ == "__main__":
    try:
        """"""
        servoObj = servo.Servo(
            pca.channels[13], min_pulse=500, max_pulse=2400)
        sc = ServoThreadObject(servoObject=servoObj)
        sc.start()
        time.sleep(2)
        sc.angle = 0
        time.sleep(2)
        sc.angle = 90
        time.sleep(2)
    except KeyboardInterrupt:
        """"""
        sc.killServoThread()
        sc.join()
