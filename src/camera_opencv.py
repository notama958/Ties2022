# upgrade version of color detection
# use for rastank
# author: yen tran
# license: Adeept

import os
from tkinter import W
import cv2
from base_camera import BaseCamera
import numpy as np
import threading
from vision import lidar_litev3_thread
import time
import speaker

from utils import stack
# from stack import ColorStack
# Servo
from arm import Servos
# Motors
from wheel import Move
# Canny thresholds
CANNY_T1 = 150
CANNY_T2 = 150
# min contour Area
AREA = 5000
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
BLUE = 0
GREEN = 1
RED = 2


BGR_LOW = [[80, 40, 0], [40, 80, 0], [40, 00, 80]]
BGR_HIGH = [[220, 100, 80], [100, 220, 80], [
    100, 80, 220]]
font = cv2.FONT_HERSHEY_SIMPLEX

FORE = 0
BACK = 1

# read adjustment hsv txt files
for i in colors:
    try:
        """"""
        f = open("utils/{}.txt".format(i.lower()), "r")
        lines = f.readlines()
        max = []
        min = []
        for line in lines:
            line = line.strip().split(" ")
            if "max" in line[0]:
                max.append(int(line[1]))
            elif "min" in line[0]:
                min.append(int(line[1]))
        if i == 'BLUE':
            if len(min) == len(max) and len(min) == 3:
                BLUE_LOWER = np.array(min)
                BLUE_UPPER = np.array(max)
        elif i == 'GREEN':
            if len(min) == len(max) and len(min) == 3:
                GREEN_LOWER = np.array(min)
                GREEN_UPPER = np.array(max)
        elif i == 'RED':
            if len(min) == len(max) and len(min) == 3:
                RED_LOWER = np.array(min)
                RED_UPPER = np.array(max)

    except FileNotFoundError:
        print("not found init {} file".format(i), end=" ")
        print("you should run utils/thresholds.py before running this file")
        pass

color_dict = {
    "RED": {"HIGH": RED_UPPER, "LOW": RED_LOWER},
    "GREEN": {"HIGH": GREEN_UPPER, "LOW": GREEN_LOWER},
    "BLUE": {"HIGH": BLUE_UPPER, "LOW": BLUE_LOWER},
}
print(color_dict)
# read contour.txt
try:
    """read file if have and override standard value"""
    f = open("utils/contour.txt", "r")
    lines = f.readlines()
    for line in lines:
        line = line.strip().split(" ")
        if "canny_t1" in line[0]:
            CANNY_T1 = int(line[1])
        elif "canny_t2" in line[0]:
            CANNY_T2 = int(line[1])
        elif "area" in line[0]:
            AREA = int(line[1])
except FileNotFoundError:
    """no init file found"""
    print("not found contour init file", end=" ")
    print("you should run utils/thresholds.py before running this file")
    pass
print(CANNY_T1)
print(CANNY_T2)
print(AREA)


class Camera(BaseCamera):
    video_source = 0

    def __init__(self):
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
    color_selected = GREEN  # start with the blue
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
    grabing_free = True
    # Servos,motors and lidar
    scGear = Servos.ServoCtrl()
    motors = Move.MotorThread()
    lidar = lidar_litev3_thread.Lidar()
    myVoice = speaker.Speaker()
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

    Y_lock = 0
    X_lock = 0
    tor = 17
    error_X = 0
    error_Y = 0

    shape = {
        "circle": False,
        "box": False,
    }
    areas = {
        "circle": {
            "area": 0,
            "approx": None
        },
        "box": {
            "area": 0,
            "approx": None
        },
    }

    def __init__(self, *args, **kwargs):
        self.CVThreading = 0
        self.findColorDetection = 0
        self.findcontainerDetection = 0
        self.mov_x = None
        self.mov_y = None
        self.mov_w = None
        self.mov_h = None
        # newly added
        self.color_name = colors[self.color_selected]  # save the color name
        self.stack = stack.ColorStack()
        self.stack.push(self.color_name)
        #################
        self.scGear.moveInit()
        # self.scGear.start()
        self.motors.start()
        self.lidar.start()
        self.myVoice.start()
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

    def findColorVer2(self, frame_image):
        # image smoothing
        imgblur = cv2.GaussianBlur(frame_image, (7, 7), 1)
        # to hsv
        imgHSV = cv2.cvtColor(imgblur, cv2.COLOR_BGR2HSV)
        # apply color threshold
        hsv = cv2.inRange(
            imgHSV, color_dict.get(self.color_name).get('LOW'), color_dict.get(self.color_name).get('HIGH'))

        mask = cv2.erode(hsv, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        # find contour and detect object shape
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        print("0000000000000000000000000000000000000000000")
        print(cnts)
        print("0000000000000000000000000000000000000000000")
        if len(cnts) > 0:
            self.findColorDetection = 1
            c = max(cnts, key=cv2.contourArea)
            ((self.box_x, self.box_y), self.radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            self.center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            X = int(self.box_x)
            Y = int(self.box_y)
            self.error_Y = 240 - Y
            self.error_X = 320 - X
        else:
            self.findColorDetection = 0
            self.findcontainerDetection = 0
            self.error_X = 0
            self.error_Y = 0
            self.center = 0
        # self.pause()
    # find color area based on frame

    def findColor(self, frame_image):
        """find color target"""
        # image smoothing
        imgblur = cv2.GaussianBlur(frame_image, (7, 7), 1)
        # to hsv
        imgHSV = cv2.cvtColor(imgblur, cv2.COLOR_BGR2HSV)
        # apply color threshold
        hsv = cv2.inRange(
            imgHSV, color_dict.get(self.color_name).get('LOW'), color_dict.get(self.color_name).get('HIGH'))

        # apply canny
        imgCanny = cv2.Canny(hsv, CANNY_T1, CANNY_T2)
        # erode and dilate
        kernel = np.ones((5, 5))
        # imgEro = cv2.erode(imgCanny, kernel, iterations=1)
        imgDil = cv2.dilate(imgCanny, kernel, iterations=1)
        # find contour and detect object shape
        self.contours(imgDil)

    def contours(self, mask):
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            """"""
            area = cv2.contourArea(cnt)
            # filter area
            if area >= AREA:
                # find shape
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02*peri, True)
                objCor = len(approx)
                # # create a box around the obj
                # x, y, w, h = cv2.boundingRect(approx)
                print(objCor)
                if objCor in [4, 5, 6, 7]:
                    """square or rectangle"""
                    self.shape['box'] = True
                    self.areas['box']['area'] = area
                    self.areas['box']['approx'] = approx
                    break
                elif objCor >= 8:

                    self.shape['circle'] = True
                    self.areas['circle']['area'] = area
                    self.areas['circle']['approx'] = approx
                    break
                else:
                    self.shape['box'] = False
                    self.areas['box']['area'] = 0
                    self.areas['box']['approx'] = None
                    self.shape['circle'] = False
                    self.areas['circle']['area'] = 0
                    self.areas['circle']['approx'] = None

            # else:
            #     print("GHAHAHAHAHAH")
            #     self.shape['box'] = False
            #     self.areas['box']['area'] = 0
            #     self.areas['box']['approx'] = None
            #     self.shape['circle'] = False
            #     self.areas['circle']['area'] = 0
            #     self.areas['circle']['approx'] = None
        # print(self.shape)
        if not self.shape.get("circle") and self.shape.get("box"):
            """find container"""
            print("found box")
            self.findcontainerDetection = 1
            self.findColorDetection = 0
            # create a box around the obj
            x, y, w, h = cv2.boundingRect(self.areas.get('box').get('approx'))
            self.center = (int(x+w/2), int(y+h/2))
            self.error_Y = int(self.videoH/2) - int(y+h/2)
            self.error_X = int(self.videoW/2) - int(x+w/2)

        elif self.shape.get("circle"):
            """pick object first"""
            print("found circle")
            self.findcontainerDetection = 0
            self.findColorDetection = 1
            x, y, w, h = cv2.boundingRect(
                self.areas.get('circle').get('approx'))
            self.center = (int(x+w/2), int(y+h/2))
            self.error_Y = int(self.videoH/2) - int(y+h/2)
            self.error_X = int(self.videoW/2) - int(x+w/2)
        else:
            """"""
            self.findColorDetection = 0
            self.findcontainerDetection = 0
            self.error_X = 0
            self.error_Y = 0
            self.center = 0

    def elementDraw(self, imgInput):
        # central X Y horizontals
        cv2.line(imgInput, (int(self.videoW/2), 0),
                 (int(self.videoW/2), self.videoH), (255, 255, 255), 1)
        cv2.line(imgInput, (0, int(self.videoH/2)),
                 (self.videoW, int(self.videoH/2)), (255, 255, 255), 1)
        # not found anything
        if self.findColorDetection == 0 and self.findcontainerDetection == 0:
            cv2.putText(imgInput, 'Target Detecting', (40, 60),
                        CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            self.drawing = 0

        if self.findColorDetection == 1:
            try:
                cx, cy = self.center
                self.drawing = 1
                cv2.putText(imgInput, 'Object: {} - {}'.format(self.color_name, self.areas.get('circle').get('area')), (cx-20, cy),
                            CVThread.font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                cv2.circle(imgInput, (cx, cy),
                           8, BGR_HIGH[self.color_selected], -1)
                cv2.circle(imgInput, (cx, cy),
                           4, BGR_LOW[self.color_selected], -1)
            except TypeError:
                pass
        if self.findcontainerDetection == 1:
            try:
                cx, cy = self.center
                self.drawing = 1
                x, y, w, h = cv2.boundingRect(
                    self.areas.get('box').get('approx'))
                cv2.rectangle(imgInput, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(imgInput, "Container: {} - {}".format(self.color_name, self.areas.get('box').get('area')), (x,
                            y-10), CVThread.font, 0.5, (0, 255, 0), 2)

            except TypeError:
                pass
        return imgInput

    def resetShapeFound(self):
        """reset object shape after each frame"""
        self.shape['box'] = False
        self.shape['circle'] = False

    def processFrame(self, frame_image):
        # if there is a color in the stack
        if self.stack.peek() != -1 and not self.sorted_queue.get(self.color_name):
            self.findColor(frame_image=frame_image)
            # self.findColorVer2(frame_image=frame_image)
            self.pause()
            self.resetShapeFound()
            self.objSpacing()
            self.dcMotorMove(self.error_X)
        else:
            # when every color is found
            self.findColorDetection = 0
            self.findcontainerDetection = 0
            self.resetShapeFound()
            self.motors.motorStop()

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

        if (self.lidar.get_value() > 10 and self.lidar.get_value() <= 15) and (self.findColorDetection == 1 or self.findcontainerDetection == 1):
            self.motors.motorStop()

            self.armActions()

        elif self.lidar.get_value() > 15 and (self.findColorDetection == 1 or self.findcontainerDetection == 1):
            """"""
            # print("Motors forward")
            self.myVoice.playbackThread("forward")

            self.motors.moveForward(speed=100)
        elif self.lidar.get_value() <= 5 and (self.findColorDetection == 1 or self.findcontainerDetection == 1):
            """"""
            self.myVoice.playbackThread("back")
            # print("Motors backward")

            self.motors.moveBackward(speed=100)

    def armActions(self):
        if self.findColorDetection == 1:

            self.grabing_finished = self.scGear.grab()
            # fail? move back
            timer = 3  # 3 trials

            if self.grabing_finished == False:
                self.grabing_free = True
            else:
                self.motors.moveBackward(speed=100)
                while timer > 0 and not self.grabing_finished:
                    self.motors.motorStop()
                    self.grabing_finished = self.scGear.grab()

                    if self.grabing_finished:
                        self.grabing_free = False
                        break
                    timer -= 1

            ###########
        elif self.findcontainerDetection == 1:
            # release  the object to container
            print("====>Releasing object to container")

            # return finished status
            self.grabing_free = self.scGear.release()

            # fail? move back
            timer = 3  # 3 trials

            if self.grabing_free:
                self.stack.pop()
                self.sorted_queue[self.color_name] = True
                self.motors.moveBackward(speed=100)

                # self.whichColorNext() # comment for testing 1 color only
            else:
                self.motors.moveBackward(speed=100)
                while timer > 0 and not self.grabing_free:
                    self.motors.motorStop()
                    self.grabing_free = self.scGear.release()
                    if self.grabing_free:
                        self.grabing_finished = False
                        break
                    timer -= 1
            self.motors.motorStop()

    def allColorSorted(self):
        """Check is all colors are sorted"""
        # print(self.sorted_queue)
        for color in self.sorted_queue:
            if not self.sorted_queue.get(color):
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
            # print(self.grabing_free)
            self.processFrame(self.imgCV)
            self.CVThreading = 0
