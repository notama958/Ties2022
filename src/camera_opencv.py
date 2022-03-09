# upgrade version of color detection
# use for rastank
# author: yen tran
# license: Adeept

import os
import cv2
from base_camera import BaseCamera
import numpy as np
import threading
from vision import lidar_litev3_thread
import time
import pytesseract
from pytesseract import Output

from utils import Kalman_filter
from utils import stack
# from stack import ColorStack
# Servo
from arm import Servos
# Motors
from wheel import Move

# red
RED_UPPER = np.array([10, 255, 255])
RED_LOWER = np.array([0, 50, 70])
# green
GREEN_UPPER = np.array([70, 255, 255])
GREEN_LOWER = np.array([50, 100, 100])
# blue
BLUE_UPPER = np.array([130, 255, 255])
BLUE_LOWER = np.array([110, 50, 50])
# colors
colors = ["BLUE", "GREEN", "RED"]

color_dict = {
    "RED": {"HIGH": RED_UPPER, "LOW": RED_LOWER},
    "GREEN": {"HIGH": GREEN_UPPER, "LOW": GREEN_LOWER},
    "BLUE": {"HIGH": BLUE_UPPER, "LOW": BLUE_LOWER},
}


BGR_LOW = [[80, 40, 0], [40, 80, 0], [40, 00, 80]]
BGR_HIGH = [[220, 100, 80], [100, 220, 80], [
    100, 80, 220]]
font = cv2.FONT_HERSHEY_SIMPLEX

FORE = 0
BACK = 1

VIRTUAL_VENV = "VIRTUAL_VENV"


class Camera(BaseCamera):
    video_source = 0

    def __init__(self):
        # if os.environ.get(VIRTUAL_VENV):
        #     print("getting lib from venv")
        #     Camera.set_video_source(int(os.environ[VIRTUAL_VENV]))
        super(Camera, self).__init__()

    @ staticmethod
    def set_video_source(source):
        Camera.video_source = source

    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        cvt = CVThread()
        cvt.start()

        while True:
            # read current frame
            _, img = camera.read()
            if cvt.CVThreading:
                pass
            else:
                cvt.mode(img)
                cvt.resume()

            # mark the object
            img = cvt.elementDraw(img)
            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()


class CVThread(threading.Thread):
    # newly added
    color_selected = 0  # start with the blue
    color_name = ""
    container_name = ""
    center = None
    box_x = 0
    box_y = 0
    sorted_queue = {
        "BLUE": False,
        "GREEN": False,
        "RED": False,
    }  # BGR

    grabing_finished = False
    grabing_free = False
    # Servos,motors and lidar
    scGear = Servos.ServoCtrl()
    motors = Move.MotorThread()
    lidar = lidar_litev3_thread.Lidar()
    # end of newly added
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
    error_X = 0
    error_Y = 0
    textFound = False

    def __init__(self, *args, **kwargs):
        self.CVThreading = 0
        self.findColorDetection = 0
        self.findcontainerDetection = 0
        self.radius = 0
        self.mov_x = None
        self.mov_y = None
        self.mov_w = None
        self.mov_h = None
        # newly added
        self.color_selected = 1  # init color is BLUE
        self.color_name = colors[self.color_selected]  # save the color name
        self.stack = stack.ColorStack()
        self.stack.push(self.color_name)
        #################
        self.scGear.moveInit()
        # self.scGear.start()
        self.motors.start()
        self.lidar.start()
        ##############
        # end of newly added
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
        # self.resume()

    # find color and draw a mark at target

    def elementDraw(self, imgInput):
        # central X Y horizontals
        cv2.line(imgInput, (int(self.videoW/2), 0),
                 (int(self.videoW/2), self.videoH), (255, 255, 255), 1)
        cv2.line(imgInput, (0, int(self.videoH/2)),
                 (self.videoW, int(self.videoH/2)), (255, 255, 255), 1)
        if self.findColorDetection == 0 and self.findcontainerDetection == 0:
            cv2.putText(imgInput, 'Target Detecting', (40, 60),
                        CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            self.drawing = 0

        if self.findColorDetection == 1:
            if self.radius > 10:
                try:
                    cx, cy = self.center
                    self.drawing = 1
                    cv2.putText(imgInput, 'Target Detected {}'.format(self.color_name), (cx+10, cy),
                                CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.circle(imgInput, (cx, cy),
                               8, BGR_HIGH[self.color_selected], -1)
                    cv2.circle(imgInput, (cx, cy),
                               4, BGR_LOW[self.color_selected], -1)
                except TypeError:
                    pass
        if self.findcontainerDetection == 1:
            if self.textFound:
                try:
                    """"""
                    cx, cy = self.center
                    self.drawing = 1
                    cv2.putText(imgInput, 'Target Detected {}'.format(self.container_name), (cx+10, cy),
                                CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.circle(imgInput, (cx, cy),
                               8, BGR_HIGH[self.color_selected], -1)
                    cv2.circle(imgInput, (cx, cy),
                               4, BGR_LOW[self.color_selected], -1)
                except TypeError:
                    pass
        return imgInput

    def findColor(self, frame_image):
        """find color target"""
        hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(
            hsv, color_dict.get(self.color_name).get('LOW'), color_dict.get(self.color_name).get('HIGH'))  # 1
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(cnts) > 0:
            self.findColorDetection = 1
            # find the max area
            c = max(cnts, key=cv2.contourArea)
            ((self.box_x, self.box_y),
             self.radius) = cv2.minEnclosingCircle(c)

            M = cv2.moments(c)
            # center coordinate
            self.center = (int(M["m10"] / M["m00"]),
                           int(M["m01"] / M["m00"]))
            X = 0
            Y = 0
            try:
                X, Y = self.center
            except TypeError:
                pass
            self.error_Y = int(self.videoH/2) - Y
            self.error_X = int(self.videoW/2) - X
            # print(self.error_X)

        else:
            self.findColorDetection = 0
            self.error_X = 0
            self.error_Y = 0
            self.center = 0
            self.radius = 0

    def findContainer(self, frame_image):
        """Find container destination"""
        # SUPER SLOW NEED TO CHANGE
        data = pytesseract.image_to_data(
            frame_image, output_type=Output.DICT)
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 60:
                (text, x, y, w, h) = (data['text'][i], data['left']
                                      [i], data['top'][i], data['width'][i], data['height'][i])
                # don't show empty text
                # print(text)
                if text and text.strip() != "":
                    self.findcontainerDetection = 1
                    self.textFound = True
                    self.center = (x, y)
                    self.error_Y = int(self.videoH/2) - x
                    self.error_X = int(self.videoW/2) - y
                else:
                    self.textFound = False
                    self.center = 0

    def processFrame(self, frame_image):
        # if there is a color in the stack
        if self.stack.peek() != -1:
            if self.grabing_free:
                """when arm is free"""
                self.findColor(frame_image=frame_image)
                self.pause()
            elif not self.grabing_free:
                """when arm is holding an object"""
                # print("find box container {}".format(
                #     colors[self.color_selected]))
                self.findContainer(frame_image=frame_image)
                self.pause()

            # # control servo at camera (Adeept)
            # self.servoMove(
            # CVThread.T_servo, CVThread.T_direction, self.error_Y)
            # # move wheels
            # self.objSpacing()
            # self.dcMotorMove(self.error_X)
        else:
            # when every color is found
            self.findColorDetection = 0
            # self.motors.motorStop()

    # fix this one to use both color and text
    def dcMotorMove(self, calCenter):
        """
            calCenter <0 => object is on the left
            calCenter >0 => object is on the right

        """
        self.motors.updateE(calCenter)  # keep track of the error
        if abs(calCenter) > 100:
            if calCenter < 0:
                self.motors.turnRight(100)
            elif calCenter > 0:
                self.motors.turnLeft(100)
        else:
            self.motors.motorStop()
        # print(calCenter)

    # fix this one to use both color and text
    def objSpacing(self):
        if (self.lidar.get_value() > 10 and self.lidar.get_value() <= 15) and (self.findColorDetection == 0 or self.findcontainerDetection == 0):
            self.motors.motorStop()

            self.armActions()

        elif self.lidar.get_value() > 15 and (self.findColorDetection == 1 or self.findcontainerDetection == 1):
            """"""
            # print("Motors forward")
            # speaker.getVoice("move_forward.mp3")

            self.motors.moveForward(speed=100)
        elif self.lidar.get_value() <= 5 and (self.findColorDetection == 1 or self.findcontainerDetection == 1):
            """"""
            # speaker.getVoice("move_backward.mp3")
            # print("Motors backward")

            self.motors.moveBackward(speed=100)

    def armActions(self):
        if self.grabing_free and self.findColorDetection == 1:

            self.grabing_finished = self.scGear.grab()
            timer = 3  # 3 trials
            # fail? move back
            self.motors.moveBackward(speed=100)
            while timer > 0 and not self.grabing_finished:
                self.grabing_finished = self.scGear.grab()

                if self.grabing_finished:
                    self.grabing_free = False
                    break
                timer -= 1
            if self.grabing_finished == False:
                self.grabing_free = True
            # self.grabing_free = False
            # self.grabing_finished = False
            ###########
        elif not self.grabing_free and self.findcontainerDetection == 1:
            # release  the object to container
            print("====>Releasing object to container")

            # code for arm servos
            # return finished status
            self.grabing_free = self.scGear.release()

            # self.grabing_finished = True
            # self.grabing_free = True
            if self.grabing_free:
                self.stack.pop()
                self.sorted_queue[self.color_name] = True
                # self.whichColorNext() # comment for testing 1 color only

    def allColorSorted(self):
        """Check is all colors are sorted"""
        print(self.sorted_queue)
        for color in self.sorted_queue:
            if not self.sorted_queue[color]:
                return False
        return True

    def whichColorNext(self):
        """Define which color should be next in the stack"""
        if self.allColorSorted():
            """Stop the car"""
            print("all color sorted")

        elif not self.sorted_queue.get(colors[(self.color_selected+1) % len(colors)
                                              ]):
            """Add new color to stack"""
            self.color_selected = (self.color_selected+1) % len(colors)
            self.color_name = colors[self.color_selected]
            self.stack.push(self.color_name)

    def pause(self):
        self.__flag.clear()
        self.CVThreading = 0

    def resume(self):
        self.__flag.set()

    def run(self):
        while 1:
            self.__flag.wait()
            self.CVThreading = 1
            # CVThread.dist.checkdist()
            # self.doOpenCV(self.imgCV)
            self.processFrame(self.imgCV)
            self.CVThreading = 0
