# upgrade version of color detection
# use for rastank
# author: yen tran

import os
import imutils
import cv2
from base_camera import BaseCamera
import numpy as np
import threading
import time
# speaker
from voice import speaker_v2
# stack class
from utils import stack
# lidar
from vision import lidar_litev3_thread
# Servo
from arm import Servos
# Motors
from wheels import Move
# arduino
from utils import arduino
# Canny thresholds
CANNY_T1 = 150
CANNY_T2 = 150
# min contour Area
AREA = 3000
# red
RED_UPPER = np.array([9, 255, 255])
RED_LOWER = np.array([0, 48, 46])
# green
GREEN_UPPER = np.array([83, 255, 255])
GREEN_LOWER = np.array([53, 71, 78])
# blue
BLUE_UPPER = np.array([130, 255, 255])
BLUE_LOWER = np.array([104, 53, 32])
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

# # read adjustment hsv txt files
# for i in colors:
#     try:
#         """"""
#         f = open("utils/{}.txt".format(i.lower()), "r")
#         lines = f.readlines()
#         min = None
#         max = None

#         for line in lines:
#             line = line.strip().split(" ")
#             if "max" in line[0]:
#                 max = np.array([int(line[1]), int(line[2]), int(line[3])])
#             elif "min" in line[0]:
#                 min = np.array([int(line[1]), int(line[2]), int(line[3])])

#         if i == 'BLUE':
#             if len(min) == len(max) and len(min) == 3:
#                 BLUE_LOWER = min
#                 BLUE_UPPER = max
#         elif i == 'GREEN':
#             if len(min) == len(max) and len(min) == 3:
#                 GREEN_LOWER = min
#                 GREEN_UPPER = max
#         elif i == 'RED':
#             if len(min) == len(max) and len(min) == 3:
#                 RED_LOWER = min
#                 RED_UPPER = max

#     except FileNotFoundError:
#         print("not found init {} file".format(i), end=" ")
#         print("you should run utils/thresholds.py before running this file")
#         pass

color_dict = {
    "RED": {"HIGH": RED_UPPER, "LOW": RED_LOWER},
    "GREEN": {"HIGH": GREEN_UPPER, "LOW": GREEN_LOWER},
    "BLUE": {"HIGH": BLUE_UPPER, "LOW": BLUE_LOWER},
}
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
    color_selected = BLUE  # start with the blue
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
    myVoice = speaker_v2.Speaker()
    ard = arduino.ArduinoControl()
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
    counter = 0
    # set this where you put your box and ball
    box_cor = 220
    ball_cor = 190
    ######
    at_box = False
    at_ball = True
    rot_lock = False
    speed = 50

    def __init__(self, *args, **kwargs):
        self.CVThreading = 0
        self.findColorDetection = 0
        self.findContainerDetection = 0
        self.color_name = colors[self.color_selected]  # save the color name
        self.stack = stack.ColorStack()
        self.stack.push(self.color_name)
        #################
        self.scGear.start()
        self.motors.start()
        self.motors.setCordinate(self.box_cor, self.ball_cor)
        self.lidar.start()
        self.myVoice.start()
        self.ard.start()
        ##############
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
                # print(objCor)
                if objCor in [4, 5]:
                    """square or rectangle"""
                    self.shape['box'] = True
                    self.areas['box']['area'] = area
                    self.areas['box']['approx'] = approx
                    self.counter = 0
                    break
                elif objCor >= 8:

                    self.shape['circle'] = True
                    self.areas['circle']['area'] = area
                    self.areas['circle']['approx'] = approx
                    self.counter = 0
                    break
                else:
                    self.shape['box'] = False
                    self.areas['box']['area'] = 0
                    self.areas['box']['approx'] = None
                    self.shape['circle'] = False
                    self.areas['circle']['area'] = 0
                    self.areas['circle']['approx'] = None
        # print(self.shape)
        if not self.shape.get("circle") and self.shape.get("box"):
            """find container"""
            #print("found box")
            self.findContainerDetection = 1
            self.findColorDetection = 0
            # create a box around the obj
            x, y, w, h = cv2.boundingRect(self.areas.get('box').get('approx'))
            self.center = (int(x+w/2), int(y+h/2))
            self.error_Y = int(self.videoH/2) - int(y+h/2)
            self.error_X = int(self.videoW/2) - int(x+w/2)

        elif self.shape.get("circle"):
            """pick object first"""
            #print("found circle")
            self.findContainerDetection = 0
            self.findColorDetection = 1
            x, y, w, h = cv2.boundingRect(
                self.areas.get('circle').get('approx'))
            self.center = (int(x+w/2), int(y+h/2))
            self.error_Y = int(self.videoH/2) - int(y+h/2)
            self.error_X = int(self.videoW/2) - int(x+w/2)
        else:
            """"""
            self.findColorDetection = 0
            self.findContainerDetection = 0
            self.error_X = 0
            self.error_Y = 0
            self.center = 0
            self.counter += 1

    def elementDraw(self, imgInput):
        # central X Y horizontals
        cv2.line(imgInput, (int(self.videoW/2), 0),
                 (int(self.videoW/2), self.videoH), (255, 255, 255), 1)
        cv2.line(imgInput, (0, int(self.videoH/2)),
                 (self.videoW, int(self.videoH/2)), (255, 255, 255), 1)
        # not found anything
        if self.findColorDetection == 0 and self.findContainerDetection == 0:
            cv2.putText(imgInput, 'Target Detecting', (40, 60),
                        CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            self.drawing = 0
        # found the object
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
        # found the container
        if self.findContainerDetection == 1:
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
        """process each frame"""
        # if there is a color in the stack
        if self.stack.peek() != -1 and not self.sorted_queue.get(self.color_name):
            self.findColor(frame_image=frame_image)
            self.pause()
            self.objSpacing()
            self.dcMotorMove(self.error_X)
            self.resetShapeFound()
        else:
            # when every color is found
            self.findColorDetection = 0
            self.findContainerDetection = 0
            self.resetShapeFound()
            self.motors.motorStop()

    def dcMotorMove(self, calCenter):
        """
            calCenter = screen's X - target's X

        """
        self.motors.updateE(calCenter)  # keep track of the error
        if abs(calCenter) > 100:
            if calCenter < 0:
                # print("turn right")
                self.motors.turnRight(self.speed)
            elif calCenter > 0:
                # print("turn left")
                self.motors.turnLeft(self.speed)
        else:
            self.motors.motorStop()
        # print(calCenter)

    def objSpacing(self):
        """spacing between the robot and target"""
        if (self.lidar.get_value() > 15 and self.lidar.get_value() <= 30) and (self.findColorDetection == 1 or self.findContainerDetection == 1):

            self.motors.motorStop()

            # print("STOP")
            self.armActions()

        elif self.lidar.get_value() > 30 and (self.findColorDetection == 1 or self.findContainerDetection == 1):
            """"""
            #print("move forward")
            self.motors.moveForward(speed=self.speed)
        elif self.lidar.get_value() <= 15 and (self.findColorDetection == 1 or self.findContainerDetection == 1):
            """"""
            #print("move back")

            self.motors.moveBackward(speed=self.speed)

    def armActions(self):
        if self.findColorDetection == 1:

            self.grabing_finished = self.scGear.grab_v2()
            # fail? move back
            timer = 3  # 3 trials

            if self.grabing_finished == False:
                self.myVoice.playbackThread(self.color_selected)
                self.grabing_free = True
            else:
                self.motors.moveBackward(speed=self.speed)
                while timer > 0 and not self.grabing_finished:
                    self.motors.motorStop()
                    self.grabing_finished = self.scGear.grab_v2()

                    if self.grabing_finished:
                        self.grabing_free = False
                        break
                    timer -= 1

            ###########
        elif self.findContainerDetection == 1:
            # release  the object to container
            print("====>Releasing object to container")

            # return finished status
            self.grabing_free = self.scGear.release_v2()

            # fail? move back
            timer = 3  # 3 trials

            if self.grabing_free:
                self.myVoice.playbackThread(4)
                self.stack.pop()
                # self.sorted_queue[self.color_name] = True ## comment for looping
                self.motors.moveBackward(speed=self.speed)
                # move to take next color
                self.motors.findBallPos(self.ball_cor, self.speed)
                self.whichColorNext()  # comment for testing 1 color only
                self.ard.runSolenoid()  # run the solenoid clapping performance
            else:
                self.motors.moveBackward(speed=self.speed)
                while timer > 0 and not self.grabing_free:
                    self.motors.motorStop()
                    self.grabing_free = self.scGear.release_v2()
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

            if self.counter > 100 and self.findContainerDetection == 0 and self.findColorDetection == 0 and not self.rot_lock:
                self.rot_lock = True
                self.findColorDetection = 0
                self.findContainerDetection = 0
                # depend on what angle it is
                self.rot_lock = self.motors.findCordinate(speed=self.speed)
                self.at_box = True
                self.at_ball = False
                self.counter = 0
            self.processFrame(self.imgCV)
            self.CVThreading = 0
