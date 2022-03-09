import numpy as np
import cv2

# here insert the bgr values which you want to convert to hsv
green = np.uint8([[[0, 255, 0]]])
red = np.uint8([[[0, 0, 255]]])
blue = np.uint8([[[255, 0, 0]]])


def convertBGR(bgr):

    hsvGreen = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    lowerLimit = hsvGreen[0][0][0] - 10, 100, 100
    upperLimit = hsvGreen[0][0][0] + 10, 255, 255

    print(upperLimit)
    print(lowerLimit)


print("green")
convertBGR(green)
print("red")
convertBGR(red)
print("blue")
convertBGR(blue)
