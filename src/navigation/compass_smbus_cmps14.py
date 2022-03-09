# Author: Yen Tran
# hardware : HMC5883L gy-271
# docs:
import logging
import math
import smbus
import time
import sys
from micropython import const

_ADDR = const(0x60)  # compass default address

# configuration
_REG_ACQ_COMMAND_HIGH = const(0x02)  # config mode 1
_REG_ACQ_COMMAND_LOW = const(0x03)  # config mode 2


class Compass():

    def __init__(self, bus_num):
        try:
            self.bus = smbus.SMBus(bus_num)
            time.sleep(0.5)
        except:
            raise RuntimeError(
                "Not found Address in I2c bus {}".format(bus_num))

    @property
    def read_compass(self):
        """"""
        high = self.bus.read_byte_data(_ADDR, _REG_ACQ_COMMAND_HIGH)
        low = self.bus.read_byte_data(_ADDR, _REG_ACQ_COMMAND_LOW)
        bearing = ((high << 8) | low)
        degree = bearing*360/3599
        return round(degree)


if __name__ == "__main__":
    compass = Compass(4)

    while True:
        print(compass.read_compass)
        time.sleep(0.5)
