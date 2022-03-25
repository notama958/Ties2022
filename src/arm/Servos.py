# Servos is used for ARM control
import busio
from board import SCL, SDA
import threading
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
import getopt
import time
import sys
import os
curr_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(curr_folder)

from ServoThread import ServoThreadObject

# print(curr_folder)

i2c = busio.I2C(SCL, SDA)


# https://circuitpython.readthedocs.io/projects/pca9685/en/latest/examples.html


pca = PCA9685(i2c)
pca.frequency = 50


def parse():
    f = open(curr_folder+"/config.txt", "r")
    lines = f.readlines()
    new_arr = []
    for line in lines:
        line = line.strip()
        if line.isdigit():
            """"""
            new_arr.append(int(line))
    return new_arr


class ServoCtrl():
    """Used servos 11,12,13,14,15"""
    global inThread
    global servoThreads
    global nowPos
    global lastPos
    global minPos
    global bufferPos
    global maxPos
    maxPulse = 2400
    minPulse = 500
    angleRange = 180
    servosID = dict(zip(range(0, 16), range(1, 16)))  # [11,15]
    servos = [None]*16
    # status
    grabing_free = True

    def __init__(self, *args, **kwargs):
        '''
                scMode: 'init' 'grab' 'release'
        '''
        self.scMode = 'init'
        self.scSteps = 30

        self.scDelay = 0.03  # smooth delay
        self.scMoveTime = 0.03  # smooth delay
        self.nowPos = [0]*16
        self.lastPos = [0]*16
        self.minPos = [0]*16
        self.maxPos = [180]*16
        # get list of active servo ids
        self.activeServos = parse()
        self.initConfig()  # instantiate all Servo object for all 16 servo pins

    def pause(self):
        print('......................pause..........................')
        self.__flag.clear()

    def resume(self):
        print('resume')
        self.__flag.set()

    def initConfig(self):
        """
            Initial setup
            should be call in init
        """
        # init selected servos from 0-15
        for i in self.activeServos:
            Servo = servo.Servo(
                pca.channels[i], min_pulse=self.minPulse, max_pulse=self.maxPulse)
            self.servos[i] = ServoThreadObject(servoObject=Servo)
            self.servos[i].start()
        # print(self.servos)
        self.moveInit()

    def moveInit(self):
        """move all servos to center"""
        for i in self.activeServos:
            self.servos[i].moveAngle(90)

    def setDelay(self, delaySet):
        self.scDelay = delaySet

    def moveAngle(self, ID, angleInput):
        """move servo to specific angle"""
        self.nowPos[ID] = angleInput
        if self.nowPos[ID] > self.maxPos[ID]:
            self.nowPos[ID] = self.maxPos[ID]
        elif self.nowPos[ID] < self.minPos[ID]:
            self.nowPos[ID] = self.minPos[ID]
        self.lastPos[ID] = self.nowPos[ID]
        self.servos[ID].moveAngle(self.nowPos[ID])  # set new value to servo

    def grab(self):
        """grab object in front of"""
        try:

            self.moveAngle(0, 0)
            self.moveAngle(13, 10)
            self.moveAngle(12, 40)

            time.sleep(1)
            self.moveAngle(0,  135)
            time.sleep(1.5)
            print("rise up the hand")
            # rise up the hand
            self.moveAngle(13, 60)
            self.moveAngle(12, 40)
            self.grabing_free = False

        except Exception:
            self.grabing_free = True

        return self.grabing_free

        # raise('Thread failed')
    def test(self):
        try:
            """"""
            self.moveAngle(0, 0)
            self.moveAngle(13, 10)
            self.moveAngle(12, 40)

            time.sleep(0.5)
            self.moveAngle(0,  135)
            time.sleep(0.5)
            print("rise up the hand")
            # rise up the hand
            self.moveAngle(13, 90)
            self.moveAngle(12, 0)
            time.sleep(0.20)
            self.moveAngle(0,  0)
        except Exception:
            """"""

    def release(self):
        """release object in front of"""
        try:
            self.moveAngle(13, 60)
            self.moveAngle(12, 40)
            self.moveAngle(1, 90)
            self.moveAngle(0, self.minPos[0])
            time.sleep(3)
            self.scMode = 'init'
            self.grabing_free = True
        except Exception:
            self.grabing_free = False
        return self.grabing_free

    def killServoThread(self, ID):
        self.servos[ID].join()

    def pauseServoThread(self, ID):
        self.servos[ID].pause()

    def scMove(self):
        """Use for input command"""
        if self.scMode == 'init':
            self.moveInit()
        elif self.scMode == 'grab':
            if self.grabing_free == True:
                self.grab()
        elif self.scMode == 'release':
            for i in self.activeServos:
                self.pauseServoThread(i)
            self.release()

    def destroy(self):
        """Clean PCA"""
        for i in self.activeServos:
            self.killServoThread(i)
        pca.deinit()


def getServoPins(argv):
    if len(argv) <= 1 or (len(argv) <= 3 and len(argv) > 1):
        raise Exception('plz enter enough servos pins')
    else:
        return argv[1], argv[2], argv[3]


if __name__ == "__main__":
    # sc = ServoCtrl()
    sc = ServoCtrl()
    try:
        """"""
        # arr = [None]*16

        sc.moveInit()
        print("grab")
        # sc.grab()
        sc.test()
        # sc.moveInit()
        time.sleep(5)
        print("release")
        sc.release()
    except KeyboardInterrupt:
        """"""
        sc.destroy()
        # sc.join()
