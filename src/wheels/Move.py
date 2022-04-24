#!/usr/bin/env python3
# File name   : move.py
# Description : Control Motor
# Product     : GWR
# Website     : www.gewbot.com
# Author      : William
# Modified    : yen tran
# Date        : 2019/07/24

from navigation import compass_smbus_cmps14
import threading
import time
import os
import sys
import RPi.GPIO as GPIO

curr_folder = os.path.dirname(os.getcwd())
sys.path.append(curr_folder)
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

    def findContainerPos(self, angle=20):
        if abs(self.currentDir - angle) > 5:
            self.moveBackward(80)
        time.sleep(1)
        self.rotate(angle)
        return False

    def findBallPos(self, angle=20):
        if abs(self.currentDir - angle) > 5:
            self.moveBackward(80)
        time.sleep(1)
        self.rotate(angle)
        return False

    def rotate(self, dest):
        """rotate to specific angle"""
        # read compass value
        self.setLock(False)

        # set lock for while loop
        time.sleep(0.5)

        calc = self.currentDir-dest

        while 1:
            """"""
            if abs(self.currentDir-dest) <= 5:
                print("STOP")
                self.motorStop()
                break
            if abs(calc) <= 180:
                if self.currentDir > dest:
                    self.turnLeft(100)
                elif self.currentDir < dest:
                    self.turnRight(100)
            else:
                if calc > 0:
                    self.turnRight(100)
                else:
                    self.turnLeft(100)
            time.sleep(0.3)
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
        speed_set = 100
        motors = MotorThread()
        motors.start()
        motors.setup()
        ball = 90
        box = 30
        # motors.turnRight(100)
        # time.sleep(1)
        # motors.turnLeft(100)
        # time.sleep(1)

        # motors.setLock()
        motors.findContainerPos(box)
        time.sleep(1)
        motors.findBallPos(ball)

        time.sleep(2)
        # motors.findBallPos(270)
        time.sleep(1)
        motors.findContainerPos(box)
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
