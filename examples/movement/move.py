#!/usr/bin/env python3
# File name   : move.py
# Description : Control Motor
# Product     : GWR
# Website     : www.gewbot.com
# Author      : William
# Date        : 2019/07/24
import threading
import time
import RPi.GPIO as GPIO

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

    def __init__(self, *args, **kwargs):
        super(MotorThread, self).__init__(*args, *kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()

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
        while 1:
            self.__flag.wait()
            self.trackObj()
            pass

    def updateE(self, e):
        self.errorX = e

    def currentE(self):
        return self.errorX

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
        self.__flag.clear()

    def resume(self):
        print('resume')
        self.__flag.set()

    def moveForward(self, speed=50):
        self.motor_left(1, Dir_backward, speed)
        self.motor_right(1, Dir_forward, speed)
        time.sleep(0.2)

    def moveBackward(self, speed=50):
        self.motor_left(1, Dir_forward, speed)
        self.motor_right(1, Dir_backward, speed)
        time.sleep(0.2)

    def turnRight(self, speed=80):
        self.motor_left(1, Dir_forward, speed)
        self.motor_right(1, Dir_forward, speed)
        time.sleep(0.2)

    def turnLeft(self, speed=80):
        self.motor_left(1, Dir_backward, speed)
        self.motor_right(1, Dir_backward, speed)
        time.sleep(0.2)

    def destroy(self):
        self.motorStop()
        GPIO.cleanup()             # Release resource


if __name__ == '__main__':
    try:
        speed_set = 60
        motors = MotorThread()
        motors.start()
        motors.setup()
        time.sleep(1.3)
        motors.motorStop()
        motors.destroy()
    except KeyboardInterrupt:
        motors.destroy()
