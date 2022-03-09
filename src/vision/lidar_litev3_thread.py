import threading
import time
import board
import sys
import os
curr_folder = os.path.dirname(os.path.realpath(__file__))

sys.path.append(curr_folder)

import lidar_smbus
# https://circuitpython.readthedocs.io/projects/lidarlite/en/latest/api.html


class Lidar(threading.Thread):
    """Lidar control"""
    lidar_scl = 3
    lidar_sda = 2

    def __init__(self, *args, **kwargs):
        # Create library object using our Bus I2C port
        # gpio 2 and 3
        super(Lidar, self).__init__(*args, *kwargs)
        # remove adafruit
        # self.i2c = busio.I2C(self.lidar_scl, self.lidar_sda)
        # self.sensor = adafruit_lidarlite.LIDARLite(self.i2c)

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
                # this sometimes throw  Measurement undefined
                self.lidar_value = self.sensor.distance
                #print(self.get_value())
                #print(self.get_value())
            except RuntimeError:
                self.lidar_value = 0

    def get_value(self):
        # get lidar latest value
        return self.lidar_value

    def pause(self):
        print('......................pause..........................')
        # set to false
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
