from __future__ import division
import time
import sys
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import threading

from board import SCL, SDA
import busio
i2c = busio.I2C(SCL, SDA)
'''
change this form 1 to -1 to reverse servos
'''


pca = PCA9685(i2c)
pca.frequency = 50
servo7 = servo.Servo(pca.channels[15], min_pulse=500, max_pulse=2400)
for i in range(180):
    servo7.angle = i
    time.sleep(0.03)
for i in range(180):
    servo7.angle = 180 - i
    time.sleep(0.03)
pca.deinit()


# class ServoCtrl(threading.Thread):
#     """Used servos 11,12,13,14,15"""
#     global inThread
#     global servoThreads
#     global nowPos
#     global lastPos
#     global minPos
#     global bufferPos
#     global maxPos
#     maxPulse = 2400
#     minPulse = 500
#     angleRange = 180
#     servosID = dict(zip(range(11, 16), range(1, 6)))  # [11,15]
#     servos = dict.fromkeys(range(11, 16))

#     def __init__(self, *args, **kwargs):

#         self.sc_direction = dict.fromkeys(range(1, 6), 0)

#         '''
# 		scMode: 'init' 'auto' 'quick'
# 		'''
#         self.scMode = 'auto'
#         self.scTime = 2.0
#         self.scSteps = 30

#         self.scDelay = 0.03
#         self.scMoveTime = 0.03
#         # running each motor control in thread
#         self.inThread = dict.fromkeys(range(11, 16), False)
#         self.servoThreads = dict.fromkeys(range(11, 16))
#         self.nowPos = dict.fromkeys(range(11, 16), 0)
#         self.lastPos = dict.fromkeys(range(11, 16), 0)
#         self.minPos = dict.fromkeys(range(11, 16), 0)
#         self.bufferPos = dict.fromkeys(range(11, 16), 0)
#         self.maxPos = dict.fromkeys(range(11, 16), 180)
#         self.goalUpdate = 0
#         self.initConfig()
#         super(ServoCtrl, self).__init__(*args, **kwargs)
#         self.__flag = threading.Event()
#         self.__flag.clear()

#     def pause(self):
#         print('......................pause..........................')
#         self.__flag.clear()

#     def resume(self):
#         print('resume')
#         self.__flag.set()

#     def initConfig(self):
#         """
#             Initial setup
#             should be call right after instantiation
#         """
#         for i in range(11, 16):
#             # init servo objects
#             Servo = servo.Servo(
#                 pca.channels[i], min_pulse=self.minPulse, max_pulse=self.maxPulse)
#             # print(Servo)
#             self.servos[i] = Servo
#         # print(self.servos)

#     def moveInit(self):
#         """move all servos to center"""
#         self.scMode = 'init'
#         for i in range(11, 16):
#             self.servos[i].angle = 90
#         self.pause()

#     def setAutoTime(self, autoSpeedSet):
#         self.scTime = autoSpeedSet

#     def setDelay(self, delaySet):
#         self.scDelay = delaySet

#     def moveAngle(self, ID, angleInput):
#         self.nowPos[ID] = angleInput
#         if self.nowPos[ID] > self.maxPos[ID]:
#             self.nowPos[ID] = self.maxPos[ID]
#         elif self.nowPos[ID] < self.minPos[ID]:
#             self.nowPos[ID] = self.minPos[ID]
#         self.lastPos[ID] = self.nowPos[ID]
#         while self.inThread[ID]:
#             print("Servo {} ".format(ID))
#             self.servos[ID].angle = self.nowPos[ID]  # set new value to servo
#             time.sleep(self.scDelay)
#             if self.inThread[ID] == False:
#                 print("Servo reset {}".format(ID))
#                 break

#     def moveAngleThread(self, ID, angleInput):
#         """move one servo to specific angle input"""

#         self.inThread[ID] = True
#         t1 = threading.Thread(target=self.moveAngle, args=(ID, angleInput))
#         self.servoThreads[ID] = t1
#         self.servoThreads[ID].start()

#     def killServoThread(self, ID):
#         self.inThread[ID] = False
#         self.moveInit()
#         self.servoThreads[ID].join()

#     def moveAuto(self):
#         """to grab object with the distance 8cm and at around 5cm height in front"""

#     def scMove(self):
#         if self.scMode == 'init':
#             self.moveInit()
#         elif self.scMode == 'auto':
#             self.moveAuto()

#     def run(self):
#         while 1:
#             self.__flag.wait()
#             self.scMove()
#             pass

#     def destroy(self):
#         pca.deinit()


# if __name__ == "__main__":
#     try:
#         sc = ServoCtrl()
#         sc.start()
#         sc.moveAngleThread(12, 0)
#         sc.moveAngleThread(13, 70)
#         sc.moveAngleThread(15, 0)
#         time.sleep(1)
#         sc.moveAngleThread(15, 90)
#         time.sleep(2.5)
#         print("Stop the thread")
#         sc.killServoThread(12)
#         sc.killServoThread(13)
#         sc.killServoThread(15)
#         # time.sleep(2)
#         # sc.moveAngle(13, 0)
#     except KeyboardInterrupt:
#         sc.destroy()
