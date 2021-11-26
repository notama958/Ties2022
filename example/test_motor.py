import move
import time

from move import MotorThread
BACK = 0
FORE = 1
left_backward = 0
left_forward = 1
right_backward = 0
right_forward = 1

global errorX


def moveForward(speed):
    move.motor_left(1, FORE, speed)
    move.motor_right(1, BACK, speed)
    time.sleep(0.2)


def moveBackward(speed):
    move.motor_left(1, BACK, speed)
    move.motor_right(1, FORE, speed)
    time.sleep(0.2)


def turnRight(speed=80):
    move.motor_left(1, BACK, speed)
    move.motor_right(1, BACK, speed)
    time.sleep(0.2)


def turnLeft(speed=80):

    move.motor_left(1, FORE, speed)
    move.motor_right(1, FORE, speed)
    time.sleep(0.2)


if __name__ == '__main__':
    try:
        # speed_set = 80  # turn approx 80
        # # move approx 50 = 2cm
        # move.setup()
        # move.moveForward()
        # move.moveForward()
        # move.moveBackward()
        motors = MotorThread()
        motors.start()
        motors.setup()
        motors.moveForward()
        motors.moveForward()
        motors.moveForward()
        motors.moveForward()
        motors.moveBackward()
        # i = 1
        # while i < 10:
        #     i *= 2
        #     print(i)
        #     motors.updateE(i)
        motors.destroy()
        motors.pause()
        motors.resume()
        motors.join()

        # turnLeft(speed=speed_set)
        # turnRight(speed=speed_set)
        # turnLeft(speed=speed_set)
        # turnRight(speed=speed_set)
        # turnLeft(speed=speed_set)
        # turnRight(speed=speed_set)
        # move.motorStop()
        # time.sleep(1.3)
        # move.destroy()
    except KeyboardInterrupt:
        # move.destroy()
        motors.destroy()
        motors.resume()
