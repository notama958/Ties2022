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
import RPi.GPIO as GPIO
import os
import sys

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


class MotorThread(threading.Thread):
    errorX = 0
    currentDir = 0
    compass_lock = True  # initially we dont need to read compass
    compass = compass_smbus_cmps14.Compass(4)
    compass.start()

    def __init__(self, *args, **kwargs):
        super(MotorThread, self).__init__(*args, *kwargs)
        # init compass
        self.__flag = threading.Event()
        self.__flag.clear()
        self.__flag.set()
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
            if not self.compass_lock:
                self.currentDir = self.compass.compass_value

    def updateE(self, e):
        self.errorX = e

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
        self.__flag.clear()

    def resume(self):
        print('resume')
        self.__flag.set()

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
        time.sleep(0.7)

    def turnLeft(self, speed=80):
        self.motor_left(1, left_forward, speed-10)
        self.motor_right(1, right_forward, speed-10)
        time.sleep(0.7)

    def rotate(self, angle):
        """rotate to specific angle"""
        # read compass value
        self.compass_lock = False
        # set lock for while loop
        time.sleep(0.5)
        dest = angle
        while 1:
            """"""
            if abs(self.currentDir-dest) <= 5:
                print("STOP")
                self.motorStop()
                break
            if self.currentDir > dest:
                self.turnLeft()
            elif self.currentDir < dest:
                self.turnRight()
            time.sleep(0.3)
            print(self.currentDir)

        # pause reading compass
        self.pause()
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
        print("current direction")
        print(motors.currentDir)
        motors.rotate(0)
        # print("dest ",motors.currentDir)
        # motors.turnLeft()
        # time.sleep(0.3)
        # motors.motorStop()
        # print("move foreward")
        # motors.moveForward(100)
        # time.sleep(1)
        # print("move backward")
        # motors.moveBackward(100)
        # time.sleep(1)
        # print("move left")
        # motors.turnLeft(speed_set)
        # time.sleep(1)
        # print("move ")
        # motors.turnRight(speed_set)

        # time.sleep(1.3)
        # motors.motorStop()
        # motors.destroy()
    except KeyboardInterrupt:
        motors.destroy()
