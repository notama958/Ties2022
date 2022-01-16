#!/usr/bin/python3
# File name   : Ultrasonic.py
# Description : Detection distance and tracking with ultrasonic
# Website     : www.gewbot.com
# Author      : William
# Date        : 2019/02/23
import RPi.GPIO as GPIO
import time
import threading

# Reuse of Adeept


class UltraThread(threading.Thread):
    dist = 0

    def __init__(self, *args, **kwargs):
        super(UltraThread, self).__init__(*args, *kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()

    def run(self):
        print("Ultra Thread")
        while 1:
            # self.__flag.wait()
            self.checkdist()
            # print(self.getDist())
            # time.sleep(0.5)
            pass

    def pause(self):
        print('......................pause..........................')
        self.__flag.clear()

    def resume(self):
        print('resume')
        self.__flag.set()

    def setup(self):
        self.Tr = 11  # input terminal
        self.Ec = 8  # output terminal

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.Tr, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.Ec, GPIO.IN)
        # while 1:
        #     self.checkdist()

    def checkdist(self):  # Reading distance
        for i in range(5):  # Remove invalid test results.
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.Tr, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.Ec, GPIO.IN)
            GPIO.output(self.Tr, GPIO.LOW)
            time.sleep(0.000002)
            GPIO.output(self.Tr, GPIO.HIGH)
            time.sleep(0.000015)
            GPIO.output(self.Tr, GPIO.LOW)
            while not GPIO.input(self.Ec):
                pass
            t1 = time.time()
            while GPIO.input(self.Ec):
                pass
            t2 = time.time()
            temp = (t2-t1)*340/2
            if temp > 9 and i < 4:  # 5 consecutive times are invalid data, return the last test data
                continue
            else:
                self.dist = float("{:.2f}".format(temp*100))

    def getDist(self):
        return self.dist

    def destroy(self):
        GPIO.cleanup()             # Release resource

# def checkdist():       #Reading distance
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(Tr, GPIO.OUT,initial=GPIO.LOW)
#     GPIO.setup(Ec, GPIO.IN)
#     GPIO.output(Tr, GPIO.HIGH)
#     time.sleep(0.000015)
#     GPIO.output(Tr, GPIO.LOW)
#     while not GPIO.input(Ec):
#         pass
#     t1 = time.time()
#     while GPIO.input(Ec):
#         pass
#     t2 = time.time()
#     return round((t2-t1)*340/2,2)
#     #return (t2-t1)*340/2


if __name__ == '__main__':

    try:
        ultra = UltraThread()
        ultra.start()
        ultra.setup()

        time.sleep(1)
    except KeyboardInterrupt:
        ultra.destroy()
