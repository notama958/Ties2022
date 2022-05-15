# Author: Yen Tran
# hardware : HMC5883L gy-271
# docs:
import logging
import math
import smbus
import time
import sys
import threading
from micropython import const

_ADDR = const(0x60)  # compass default address

# configuration
_REG_CMPS_COMMAND_HIGH = const(0x02)  # config mode 1
_REG_CMPS_COMMAND_LOW = const(0x03)  # config mode 2


class Compass(threading.Thread):
    read = True
    compass_value = None

    def __init__(self, bus_num, *args, **kwargs):
        super(Compass, self).__init__(*args, **kwargs)

        try:
            self.bus = smbus.SMBus(bus_num)
            time.sleep(0.5)
        except:
            raise RuntimeError(
                "Not found Address in I2c bus {}".format(bus_num))
        self.__flag = threading.Event()
        self.__flag.clear()
        self.resume()

    def run(self):
        """"""
        # self.__flag.wait()
        while self.read:
            """"""
            self.__flag.wait()
            self.compass_value = self.read_compass
            print(self.compass_value)

    def pause(self):
        print('......................pause..........................')
        # set to false
        self.__flag.clear()

    def resume(self):
        print('......................resume..........................')
        self.__flag.set()
        self.read = True

    def destroy(self):
        self.read = False
        self.compass_value = None

    @property
    def read_compass(self):
        """"""
        high = self.bus.read_byte_data(_ADDR, _REG_CMPS_COMMAND_HIGH)
        low = self.bus.read_byte_data(_ADDR, _REG_CMPS_COMMAND_LOW)
        bearing = ((high << 8) | low)
        degree = bearing*360/3599
        return round(degree)


if __name__ == "__main__":
    try:
        compass = Compass(4)
        compass.start()

    except KeyboardInterrupt:
        compass.destroy()
        compass.join()
    # while True:
    #     print(compass.read_compass)
    #     time.sleep(0.5)
