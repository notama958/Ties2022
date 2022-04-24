# Author: Yen Tran
# lidar litev3

import smbus
import time
from micropython import const

_ADDR = const(0x62)
_REG_ACQ_COMMAND = const(0x00)
_CMD_DISTANCE_NO_BIAS = const(3)
_CMD_DISTANCE_W_BIAS = const(4)
_CMD_RESET = const(0)

# The various configuration register values, from arduino library
LIDAR_CONFIGS = (
    (0x80, 0x08, 0x00),  # default
    (0x1D, 0x08, 0x00),  # short range, high speed
    (0x80, 0x00, 0x00),  # default range, higher speed short range
    (0xFF, 0x08, 0x00),  # maximum range
    (0x80, 0x08, 0x80),  # high sensitivity & error
    (0x80, 0x08, 0xB0),
)


class LIDARlitev3():

    def __init__(self, bus_num):
        try:
            self.bus = smbus.SMBus(bus_num)
            time.sleep(0.5)
            self.bias_count = 0
            self.config(0)
        except:
            raise RuntimeError(
                "Not found Address in I2c bus {}".format(bus_num))

    def reset(self):
        """flush the buffer"""
        try:
            self.bus.write_byte_data(_ADDR, _REG_ACQ_COMMAND, _CMD_RESET)
        except OSError:
            pass
        time.sleep(1)
        # flush buffer
        for _ in range(100):
            try:
                self.read_distance(True)
            except RuntimeError:
                pass
        print("Reset finished")

    def config(self, config):
        """write default value to registers"""
        settings = LIDAR_CONFIGS[config]
        self.bus.write_byte_data(_ADDR, 0x02, settings[0])
        self.bus.write_byte_data(_ADDR, 0x04, settings[1])
        self.bus.write_byte_data(_ADDR, 0x1C, settings[2])

    def read_distance(self, bias=False):
        """read distance with bias, 1/100"""
        if bias:
            self.bus.write_byte_data(
                _ADDR, _REG_ACQ_COMMAND, _CMD_DISTANCE_W_BIAS)
        else:
            self.bus.write_byte_data(
                _ADDR, _REG_ACQ_COMMAND, _CMD_DISTANCE_NO_BIAS)
        time.sleep(0.02)
        dist = self.bus.read_i2c_block_data(_ADDR, 0x8F, 2)
        time.sleep(0.02)
        return (dist[0] << 8 | dist[1])

    def read_status(self):
        """Check the status code"""

    @property
    def distance(self):
        """Measure in cm, bias taken every 100 calls"""
        self.bias_count -= 1
        if self.bias_count < 0:
            self.bias_count = 100
        return self.read_distance(self.bias_count <= 0)


if __name__ == "__main__":
    lidar = LIDARlitev3(3)
    lidar.reset()
    # while 1:
    #     print(lidar.distance)
    # time.sleep(0.1)
