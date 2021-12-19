from src.vision.camera import Camera

import numpy as np
import cv2

if __name__ == "__main__":
    raw_image = next(Camera.frames())
    nparr = np.frombuffer(raw_image, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite("tmp.jpg", img_np)
    print("saved")