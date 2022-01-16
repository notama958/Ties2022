# Servos is used for ARM control
from __future__ import division
import time
import sys
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import threading

from board import SCL, SDA
import busio
i2c = busio.I2C(SCL, SDA)


# https://circuitpython.readthedocs.io/projects/pca9685/en/latest/examples.html


pca = PCA9685(i2c)
pca.frequency = 50


class ServoCtrl(threading.Thread):
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
    servosID = dict(zip(range(11, 16), range(1, 6)))  # [11,15]
    servos = dict.fromkeys(range(11, 16))

    def __init__(self, *args, **kwargs):
        '''
                scMode: 'init' 'auto' 'quick'
                '''
        self.scMode = 'auto'
        self.scSteps = 30

        self.scDelay = 0.03  # smooth delay
        self.scMoveTime = 0.03  # smooth delay
        # running each motor control in thread
        self.inThread = dict.fromkeys(range(11, 16), False)
        self.servoThreads = dict.fromkeys(range(11, 16))
        self.nowPos = dict.fromkeys(range(11, 16), 0)
        self.lastPos = dict.fromkeys(range(11, 16), 0)
        self.minPos = dict.fromkeys(range(11, 16), 0)
        self.bufferPos = dict.fromkeys(range(11, 16), 0)
        self.maxPos = dict.fromkeys(range(11, 16), 180)
        self.goalUpdate = 0
        self.initConfig()
        super(ServoCtrl, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()

    def pause(self):
        print('......................pause..........................')
        self.__flag.clear()

    def resume(self):
        print('resume')
        self.__flag.set()

    def initConfig(self):
        """
            Initial setup
            should be call right after init
        """
        # init servo objects from 11-15
        for i in range(11, 16):
            Servo = servo.Servo(
                pca.channels[i], min_pulse=self.minPulse, max_pulse=self.maxPulse)
            # print(Servo)
            self.servos[i] = Servo
        # print(self.servos)

    def moveInit(self):
        """move all servos to center"""
        self.scMode = 'init'
        for i in range(11, 16):
            self.servos[i].angle = 100
        self.pause()

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
        while self.inThread[ID]:
            print("Servo {} ".format(ID))
            self.servos[ID].angle = self.nowPos[ID]  # set new value to servo
            time.sleep(self.scDelay)
            if self.inThread[ID] == False:
                print("Servo reset {}".format(ID))
                break

    def moveAngleThread(self, ID, angleInput):
        """Thread: move one servo to specific angle input"""
        self.inThread[ID] = True
        t1 = threading.Thread(target=self.moveAngle, args=(ID, angleInput))
        self.servoThreads[ID] = t1
        self.servoThreads[ID].start()

    def killServoThread(self, ID):
        self.inThread[ID] = False
        self.moveInit()
        self.servoThreads[ID].join()

    def run(self):
        while 1:
            self.__flag.wait()
            self.scMove()
            pass

    def scMove(self):
        """Use for input command, but here I'm so lazy :)"""
        if self.scMode == 'init':
            self.moveInit()
        # elif self.scMode == 'auto':
        #     self.moveAuto()

    def destroy(self):
        """Clean PCA"""
        pca.deinit()


if __name__ == "__main__":
    try:
        sc = ServoCtrl()
        sc.start()
        # move to the lowest reach ( at front )
        sc.moveAngleThread(12, 0)
        sc.moveAngleThread(13, 70)
        sc.moveAngleThread(15, 0)
        time.sleep(1)
        # loose up the grippper
        sc.moveAngleThread(15, 100)
        time.sleep(2.5)
        # reset servos to angle = 0
        print("Stop the thread")
        sc.killServoThread(12)
        sc.killServoThread(13)
        sc.killServoThread(15)
        # time.sleep(2)
        # sc.moveAngle(13, 0)
    except KeyboardInterrupt:
        sc.destroy()
