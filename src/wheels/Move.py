#!/usr/bin/env python3
# File name   : move.py
# Description : Control Motor
# Product     : GWR
# Website     : www.gewbot.com
# Author      : William
# Modified    : yen tran
# Date        : 2019/07/24



import threading
import time
import os
import sys
import RPi.GPIO as GPIO

curr_folder = os.path.dirname(os.getcwd())
sys.path.append(curr_folder)
from navigation import compass_smbus_cmps14
# motor_EN_A: Pin7  |  motor_EN_B: Pin11
# motor_A:  Pin8,Pin10    |  motor_B: Pin13,Pin12
Motor_A_EN = 4
Motor_B_EN = 17

Motor_A_Pin1 = 14
Motor_A_Pin2 = 15
Motor_B_Pin1 = 27
Motor_B_Pin2 = 18

Dir_forward = 0
Dir_backward = 1

left_forward = 0
left_backward = 1

right_forward = 0
right_backward = 1

pwm_A = 0
pwm_B = 0

#### BOX : 20
#### BALL : 100


class MotorThread(threading.Thread):
    errorX = 0
    currentDir = 0
    compass_lock = True  # initially we dont need to read compass
    compass = compass_smbus_cmps14.Compass(4)
    compass.start()
    compass.pause()
    ball = 0
    box = 0

    def __init__(self, *args, **kwargs):
        super(MotorThread, self).__init__(*args, *kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()

        self.setup()

    def setup(self):  # Motor initialization
        global pwm_A, pwm_B

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Motor_A_EN, GPIO.OUT)
        GPIO.setup(Motor_B_EN, GPIO.OUT)
        GPIO.setup(Motor_A_Pin1, GPIO.OUT)
        GPIO.setup(Motor_A_Pin2, GPIO.OUT)
        GPIO.setup(Motor_B_Pin1, GPIO.OUT)
        GPIO.setup(Motor_B_Pin2, GPIO.OUT)

        self.motorStop()
        try:
            pwm_A = GPIO.PWM(Motor_A_EN, 1000)
            pwm_B = GPIO.PWM(Motor_B_EN, 1000)
        except:
            pass
        self.__flag.set()

    def setCordinate(self, box, ball):
        self.box = box
        self.ball = ball

    def motorStop(self):  # Motor stops
        GPIO.output(Motor_A_Pin1, GPIO.LOW)
        GPIO.output(Motor_A_Pin2, GPIO.LOW)
        GPIO.output(Motor_B_Pin1, GPIO.LOW)
        GPIO.output(Motor_B_Pin2, GPIO.LOW)
        GPIO.output(Motor_A_EN, GPIO.LOW)
        GPIO.output(Motor_B_EN, GPIO.LOW)

    def run(self):
        print("Motor Thread")
        while 1:
            self.__flag.wait()
            # print("hello")
            if not self.compass_lock:
                self.currentDir = self.compass.compass_value
                # print("==============>",self.currentDir)
            pass

    def updateE(self, e):
        self.errorX = e

    # Reuse from Adeept
    # Motor 2 positive and negative rotation

    def motor_left(self, status, direction, speed):
        if status == 0:  # stop
            GPIO.output(Motor_B_Pin1, GPIO.LOW)
            GPIO.output(Motor_B_Pin2, GPIO.LOW)
            GPIO.output(Motor_B_EN, GPIO.LOW)
        else:
            if direction == Dir_backward:
                GPIO.output(Motor_B_Pin1, GPIO.HIGH)
                GPIO.output(Motor_B_Pin2, GPIO.LOW)
                pwm_B.start(100)
                pwm_B.ChangeDutyCycle(speed)
            elif direction == Dir_forward:
                GPIO.output(Motor_B_Pin1, GPIO.LOW)
                GPIO.output(Motor_B_Pin2, GPIO.HIGH)
                pwm_B.start(0)
                pwm_B.ChangeDutyCycle(speed)

    # Reuse from Adeept
    # Motor 1 positive and negative rotation
    def motor_right(self, status, direction, speed):
        if status == 0:  # stop
            GPIO.output(Motor_A_Pin1, GPIO.LOW)
            GPIO.output(Motor_A_Pin2, GPIO.LOW)
            GPIO.output(Motor_A_EN, GPIO.LOW)
        else:
            if direction == Dir_forward:
                GPIO.output(Motor_A_Pin1, GPIO.HIGH)
                GPIO.output(Motor_A_Pin2, GPIO.LOW)
                pwm_A.start(100)
                pwm_A.ChangeDutyCycle(speed)
            elif direction == Dir_backward:
                GPIO.output(Motor_A_Pin1, GPIO.LOW)
                GPIO.output(Motor_A_Pin2, GPIO.HIGH)
                pwm_A.start(0)
                pwm_A.ChangeDutyCycle(speed)
        return direction

    def pause(self):
        print('......................pause..........................')
        self.compass_lock = True
        self.__flag.clear()

    def resume(self):
        print('resume')
        self.__flag.set()

    def setLock(self, mode=False):
        if mode:
            self.compass.pause()
        else:
            self.compass.resume()
        self.compass_lock = mode
        self.resume()

    def moveForward(self, speed=50):
        self.motor_left(1, left_backward, speed)
        self.motor_right(1, right_forward, speed)
        time.sleep(0.2)

    def moveBackward(self, speed=50):
        self.motor_left(1, left_forward, speed)
        self.motor_right(1, right_backward, speed)
        time.sleep(0.2)

    def turnRight(self, speed=80):
        self.motor_left(1, left_backward, speed-10)
        self.motor_right(1, right_backward, speed-10)
        time.sleep(0.2)

    def turnLeft(self, speed=80):
        self.motor_left(1, left_forward, speed-10)
        self.motor_right(1, right_forward, speed-10)
        time.sleep(0.2)

    # rotate to container angle
    def findContainerPos(self, angle=20, speed=80):
        self.setLock(False)
        if abs(self.currentDir - angle) > 5:
            self.moveBackward(speed)
        time.sleep(1)
        self.rotate(angle)
        return False

    # rotate to ball angle
    def findBallPos(self, angle=20, speed=80):
        self.setLock(False)
        if abs(self.currentDir - angle) > 5:
            self.moveBackward(speed)
        time.sleep(1)
        self.rotate(angle)
        return False

    # find the correct cordinate incase robot in wrong place
    def findCordinate(self, speed):
        """"""
        self.setLock(False)
        time.sleep(0.5)
        deltaBall = abs(self.currentDir-self.ball)
        deltaBox = abs(self.currentDir-self.box)
        if deltaBall <= 20:
            print("Find container")
            self.findContainerPos(self.box, speed)
        elif deltaBox <= 20:
            print("Find Ball")
            self.findBallPos(self.ball, speed)
        else:
            if deltaBall > deltaBox:
                print("Find container")
                self.findContainerPos(self.box, speed)
            else:
                print("Find Ball")
                self.findBallPos(self.ball, speed)
        print(self.currentDir)

    # CW rotation
    def CW(self, dest, speed=80):

        delta = self.calcDelta(dest, speed)
        while 1:
            if abs(delta) <= 10:
                break
            print(self.currentDir)
            self.turnRight(speed=speed)
            time.sleep(0.3)
            delta = self.calcDelta(dest, speed)

    # CCW rotation
    def CCW(self, dest, speed=80):
        delta = self.calcDelta(dest, speed)
        while 1:
            if abs(delta) <= 10:
                break
            print(self.currentDir)
            self.turnLeft(speed=speed)
            time.sleep(0.3)
            delta = self.calcDelta(dest, speed)

    # calculate angle differences
    def calcDelta(self, dest, speed):
        delta = 0
        if self.currentDir > 350 and dest < 10:
            delta = 360-self.currentDir+dest
        elif self.currentDir < 10 and dest > 350:
            delta = 360-dest+self.currentDir
        else:
            delta = self.currentDir-dest
        return delta

    def rotate(self, dest, speed=80):
        """rotate to specific angle"""
        # set lock for while loop
        self.setLock(False)

        time.sleep(0.5)

        calc = self.currentDir-dest

        if calc > 0:
            if abs(calc) >= 180:
                self.CW(dest=dest, speed=speed)
            else:
                self.CCW(dest=dest, speed=speed)
        else:
            if abs(calc) >= 180:
                self.CCW(dest=dest, speed=speed)
            else:
                self.CW(dest=dest, speed=speed)

        # print(self.currentDir)
        # pause reading compass
        self.pause()
        self.setLock(True)
        print("Im out")
        self.motorStop()

    def destroy(self):
        self.motorStop()
        GPIO.cleanup()             # Release resource


if __name__ == '__main__':
    try:
        speed_set = 60
        motors = MotorThread()
        motors.start()
        motors.setup()
        ball = 90
        box = 10
        motors.moveForward(speed_set)
        time.sleep(1)
        motors.motorStop()
        time.sleep(2)
        motors.moveBackward(speed_set)
        # motors.rotate(0,speed_set)
        # time.sleep(2)
        # motors.turnRight(speed_set)
        # time.sleep(1)
        # motors.turnLeft(100)
        # time.sleep(1)

        # motors.setLock()
        # motors.rotate(90)
        # motors.setLock()
        # print("move backward")
        # motors.moveForward(100)
        # time.sleep(10)
        # print("move foreward")
        # motors.moveBackward(100)
        # motos.rotate(

        time.sleep(1.3)
        motors.motorStop()
        motors.destroy()
    except KeyboardInterrupt:
        motors.motorStop()
        motors.destroy()
