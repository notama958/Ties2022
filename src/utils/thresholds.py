# getting threshold for color and contour detection

import cv2
import os
import sys
import numpy as np
import argparse

camera = cv2.VideoCapture(0)

camera.set(3, 640)
camera.set(4, 480)
camera.set(5, 30)


def empty(value):
    pass


color_file = None  # filename
hsv_threshold = {
    "h_min": 0,
    "h_max": 19,
    "s_min": 110,
    "s_max": 240,
    "v_min": 153,
    "v_max": 255
}
# read previous hsv file


def read_hsv(fin):
    try:
        file = open("{}.txt".format(fin), "r+")
        lines=file.readlines()
        print(lines)
        for line in lines:
            hsv = line.strip().split(" ")
            
            if "max" in hsv[0]:
                hsv_threshold['h_max'] = int(hsv[1])
                hsv_threshold['s_max'] = int(hsv[2])
                hsv_threshold['v_max'] = int(hsv[3])
            elif "min" in hsv[0]:
                hsv_threshold['h_min'] = int(hsv[1])
                hsv_threshold['s_min'] = int(hsv[2])
                hsv_threshold['v_min'] = int(hsv[3])
        file.close()
    except FileNotFoundError:
        pass

# save hsv file


def save_hsv(h_min, h_max, s_min, s_max, v_min, v_max):
    """save hsv threshold"""
    if color_file == None:
        print("None file name input, exit and retry")
    else:
        f = open("{}.txt".format(color_file), "w+")
        content = "max: {} {} {}\nmin: {} {} {}".format(
            h_max, s_max,  v_max, h_min, s_min, v_min)
        f.write(content)
        f.close()


def save_contour(t1, t2, area):
    """save contour thresholds"""
    file = "contour.txt"
    f = open("{}".format(file), "w+")
    content = "canny_t1 {}\ncanny_t2 {}\narea {}".format(
        t1, t2,  area)
    f.write(content)
    f.close()
# stacking images in 1 windows


def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv2.resize(
                        imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(
                        imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2:
                    imgArray[x][y] = cv2.cvtColor(
                        imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(
                    imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(
                    imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver


def getContours(img, imgContour):
    """"""
    contours, hierarchy = cv2.findContours(
        img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # min area
        areaMin = cv2.getTrackbarPos("Area", "Parameters")
        # draw if area is big
        if area >= areaMin:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
            # find shape
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02*peri, True)
            # create a box around the obj
            x, y, w, h = cv2.boundingRect(approx)
            objCor = len(approx)
            objectType = None
            print(objCor)
            if objCor == 3:
                objectType = "Tri"
            elif objCor == 4:
                aspRatio = w/float(h)
                if aspRatio > 0.98 and aspRatio < 1.03:
                    objectType = "Square"
                else:
                    objectType = "Rectangle"
            elif objCor > 4:
                objectType = "Circles"

            # draw rectangle
            cv2.rectangle(imgContour, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(imgContour, objectType, (x,
                        y-30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(imgContour, "Area: "+str(int(area)), (x,
                        y-10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)


if __name__ == "__main__":
    """parse the cmd arguments"""

    # Initialize parser
    parser = argparse.ArgumentParser("create threshold color files")
    parser.add_argument("-c", "--color", help="color name", default=None)

    # get pram
    args = parser.parse_args()
    if args.color != None:
        color_file = args.color
        try:
            read_hsv(color_file)

        except FileNotFoundError:
            """go with init hsv value"""
            pass
        # create controller threshold
        cv2.namedWindow("Parameters")
        cv2.resizeWindow("Parameters", 500, 100)
        cv2.createTrackbar("threshold1", "Parameters", 150, 255, empty)
        cv2.createTrackbar("threshold2", "Parameters", 150, 255, empty)
        cv2.createTrackbar("Area", "Parameters", 5000, 30000, empty)
        cv2.createTrackbar("Hue Min", "Parameters",
                           int(hsv_threshold.get('h_min')), 179, empty)
        cv2.createTrackbar("Hue Max", "Parameters",
                           int(hsv_threshold.get('h_max')), 179, empty)
        cv2.createTrackbar("Sat Min", "Parameters",
                           int(hsv_threshold.get('s_min')), 255, empty)
        cv2.createTrackbar("Sat Max", "Parameters",
                           int(hsv_threshold.get('s_max')), 255, empty)
        cv2.createTrackbar("Val Min", "Parameters",
                           int(hsv_threshold.get('v_min')), 255, empty)
        cv2.createTrackbar("Val Max", "Parameters",
                           int(hsv_threshold.get('v_max')), 255, empty)

        while True:
            success, img = camera.read()
            imgContour = img.copy()
            # image smoothing
            imgblur = cv2.GaussianBlur(img, (7, 7), 1)
            # to hsv
            imgHSV = cv2.cvtColor(imgblur, cv2.COLOR_BGR2HSV)
            h_min = cv2.getTrackbarPos("Hue Min", "Parameters")
            h_max = cv2.getTrackbarPos("Hue Max", "Parameters")
            s_min = cv2.getTrackbarPos("Sat Min", "Parameters")
            s_max = cv2.getTrackbarPos("Sat Max", "Parameters")
            v_min = cv2.getTrackbarPos("Val Min", "Parameters")
            v_max = cv2.getTrackbarPos("Val Max", "Parameters")
            lower = np.array([h_min, s_min, v_min])
            upper = np.array([h_max, s_max, v_max])
            # apply color threshold
            hsv = cv2.inRange(imgHSV, lower, upper)
            # canny
            threshold1 = cv2.getTrackbarPos('threshold1', "Parameters")
            threshold2 = cv2.getTrackbarPos('threshold2', "Parameters")
            imgCanny = cv2.Canny(hsv, threshold1, threshold2)
            # erode and dilate
            kernel = np.ones((5, 5))
            # imgEro = cv2.erode(imgCanny, kernel, iterations=1)
            imgDil = cv2.dilate(imgCanny, kernel, iterations=1)
            # get contours
            getContours(imgDil, imgContour)
            # view images
            imgStack = stackImages(0.5, ([img, imgHSV, imgCanny],
                                         [hsv, imgDil, imgContour]))

            cv2.imshow("result", imgStack)
            if cv2.waitKey(1000) & 0xFF == ord('q'):
                break
            if cv2.waitKey(1000) & 0xFF == ord('s'):
                print("Saving HSV...")
                print(h_min, h_max, s_min, s_max, v_min, v_max)
                save_hsv(h_min, h_max, s_min, s_max, v_min, v_max)
                print("Saving contour threshold")
                print(threshold1, threshold2,
                      cv2.getTrackbarPos("Area", "Parameters"))
                save_contour(threshold1, threshold2,
                             cv2.getTrackbarPos("Area", "Parameters"))
    else:
        print("Pls enter color file name. eg: green")
