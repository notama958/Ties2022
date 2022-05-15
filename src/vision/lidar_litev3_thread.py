

import threading
import time
import board
import sys
import os
# https://circuitpython.readthedocs.io/projects/lidarlite/en/latest/api.html

curr_folder = os.path.dirname(os.path.realpath(__file__))

sys.path.append(curr_folder)

import lidar_smbus
class Lidar(threading.Thread):
    """Lidar control"""

    def __init__(self, *args, **kwargs):
        super(Lidar, self).__init__(*args, *kwargs)
        # It's automatic config I2C address by setup.py
        # check address at sudo i2cdetect -y 3
        self.sensor = lidar_smbus.LIDARlitev3(3)
        # save lidar_value
        self.lidar_value = 0
        # pause/resume thread
        self.lock = False
        self.__flag = threading.Event()
        self.__flag.set()

    def run(self):
        print("Lidar Thread")

        while not self.lock:
            # print(self.__flag.is_set())
            self.__flag.wait()
            try:
                # update value
                self.lidar_value = self.sensor.distance
                # print(self.get_value())
            except RuntimeError:
                self.lidar_value = 0

    def get_value(self):
        # get lidar latest value
        return self.lidar_value

    def pause(self):
        print('......................pause..........................')
        self.__flag.clear()

    def resume(self):
        print('......................resume..........................')
        self.__flag.set()
        self.lock = False

    def destroy(self):
        """destroy lidar"""
        print("destroy lidar")
        # Stop the thread
        self.lock = True
        self.__flag.clear()


if __name__ == '__main__':
    """Lidar testing"""
    try:
        lidar = Lidar()
        time.sleep(1)
        lidar.start()
        time.sleep(3)

        lidar.pause()
        time.sleep(2)
        lidar.resume()

        time.sleep(2)
        lidar.pause()
        time.sleep(2)
        lidar.resume()

        time.sleep(2)
        lidar.pause()
        time.sleep(2)
        lidar.resume()

    except KeyboardInterrupt:
        lidar.destroy()
        lidar.join()
