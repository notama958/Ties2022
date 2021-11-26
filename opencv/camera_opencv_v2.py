import os
import cv2
from base_camera import BaseCamera
import numpy as np
import datetime
import time
import move
import ultra
import threading
import imutils
import Kalman_filter
import RPIservo
colorUpper = np.array([179, 255, 255])
colorLower = np.array([163, 74, 30])

font = cv2.FONT_HERSHEY_SIMPLEX

FORE = 0
BACK = 1


class Camera(BaseCamera):
    video_source = 0

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        # instantiate camera_opencv
        cvt = CVThread()
        cvt.start()
        while True:
            # # read current frame
            _, img = camera.read()
            if cvt.CVThreading:
                pass
            else:
                cvt.mode(img)
                cvt.resume()
            img = cvt.elementDraw(img)

            yield cv2.imencode('.jpg', img)[1].tobytes()


class CVThread(threading.Thread):
    font = font
    cameraDiagonalW = 64
    cameraDiagonalH = 48
    videoW = 640  # mid is 320
    videoH = 480  # mid is 240
    P_direction = -1
    T_direction = -1
    P_servo = 11
    T_servo = 11
    P_anglePos = 0
    T_anglePos = 0
    kalman_filter_X = Kalman_filter.Kalman_filter(0.01, 0.1)
    kalman_filter_Y = Kalman_filter.Kalman_filter(0.01, 0.1)
    Y_lock = 0
    X_lock = 0
    tor = 17
    scGear = RPIservo.ServoCtrl()
    scGear.moveInit()
    motors = move.MotorThread()
    motors.setup()
    dist = ultra.UltraThread()
    dist.setup()

    def __init__(self, *args, **kwargs):
        self.CVThreading = 0
        self.findColorDetection = 0
        self.radius = 0
        self.mov_x = None
        self.mov_y = None
        self.mov_w = None
        self.mov_h = None

        super(CVThread, self).__init__(*args, *kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()

    def pause(self):
        print('......................pause..........................')
        self.__flag.clear()

    def resume(self):
        print('resume')
        self.__flag.set()

    def mode(self, imgInput):
        self.imgCV = imgInput
        self.resume()

    def elementDraw(self, imgInput):  # find color and draw a retangle around the color object
        # print(imgInput)
        if self.findColorDetection:
            cv2.putText(imgInput, 'Target Detected', (40, 60),
                        CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            self.drawing = 1
        else:
            cv2.putText(imgInput, 'Target Detecting', (40, 60),
                        CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            self.drawing = 0

        if self.radius > 10 and self.drawing:
            cv2.rectangle(imgInput, (int(self.box_x-self.radius), int(self.box_y+self.radius)),
                          (int(self.box_x+self.radius), int(self.box_y-self.radius)), (255, 255, 255), 1)
        return imgInput

    def doOpenCV(self, frame_image):
        self.pause()

    def pause(self):
        self.__flag.clear()
        self.CVThreading = 0

    def resume(self):
        self.__flag.set()

    def run(self):
        while 1:
            self.__flag.wait()
            self.CVThreading = 1
            CVThread.dist.checkdist()
            # self.doOpenCV(self.imgCV)
            self.findColor(self.imgCV)
            self.CVThreading = 0

    def servoMove(ID, Dir, errorInput):  # deo hieu
        if ID == 1:
            errorGenOut = CVThread.kalman_filter_X.kalman(errorInput)
            CVThread.P_anglePos += 0.15 * \
                (errorGenOut*Dir)*CVThread.cameraDiagonalW/CVThread.videoW

            if abs(errorInput) > CVThread.tor:
                CVThread.scGear.moveAngle(ID, CVThread.P_anglePos)
                CVThread.X_lock = 0
            else:
                CVThread.X_lock = 1
        elif ID == 11:
            errorGenOut = CVThread.kalman_filter_Y.kalman(errorInput)
            CVThread.T_anglePos += 0.1 * \
                (errorGenOut*Dir)*CVThread.cameraDiagonalH/CVThread.videoH

            if abs(errorInput) > CVThread.tor:
                CVThread.scGear.moveAngle(ID, CVThread.T_anglePos)
                CVThread.Y_lock = 0
            else:
                CVThread.Y_lock = 1
        else:
            print('No servoPort %d assigned.' % ID)

    def dcMotorMove(calCenter):  # move sao  ma??? + ket hop voi utra dist=20cm
        """"""
        CVThread.motors.updateE(calCenter)
        if abs(calCenter) > 50:
            if calCenter < 0:
                CVThread.motors.turnLeft(speed=60)
            elif calCenter > 0:
                CVThread.motors.turnRight(speed=60)
        else:
            CVThread.motors.motorStop()
        # print(calCenter)

    def objSpacing():
        print(CVThread.dist.getDist())
        if CVThread.dist.getDist() > 18 and CVThread.dist.getDist() < 22:
            CVThread.motors.motorStop()

        elif CVThread.dist.getDist() > 20:
            CVThread.motors.moveForward()
        else:
            CVThread.motors.moveBackward()

    def findColor(self, frame_image):
        hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, colorLower, colorUpper)  # 1
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        # print(cnts)
        center = None
        if len(cnts) > 0:
            self.findColorDetection = 1
            c = max(cnts, key=cv2.contourArea)
            ((self.box_x, self.box_y), self.radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            X = int(self.box_x)
            Y = int(self.box_y)
            global error_X
            global error_Y
            error_Y = 240 - Y
            error_X = 320 - X
            # CVThread.servoMove(CVThread.P_servo, CVThread.P_direction, error_X)
            CVThread.servoMove(CVThread.T_servo, CVThread.T_direction, error_Y)
            CVThread.dcMotorMove(error_X)
            CVThread.objSpacing()

            # while abs(error_X) > 3:
            #     if error_X < 0:
            #         move.turnRight()
            #     elif error_X > 0:
            #         move.turnLeft()
            # # if CVThread.X_lock == 1 and CVThread.Y_lock == 1:
            # if CVThread.Y_lock == 1:
            #     led.setColor(255, 78, 0)
            #     # switch.switch(1,1)
            #     # switch.switch(2,1)
            #     # switch.switch(3,1)
            # else:
            #     led.setColor(0, 78, 255)
            #     # switch.switch(1,0)
            #     # switch.switch(2,0)
            #     # switch.switch(3,0)
        else:
            self.findColorDetection = 0
            self.motors.motorStop()
        self.pause()
