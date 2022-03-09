# Author: Yen Tran
# hardware : HMC5883L gy-271
# docs:
import logging
import math
import smbus
import time
import sys
from micropython import const

_ADDR = const(0x1E)  # compass default address
_CMD_RESET = const(0x0B)  # reset
_STATUS = const(0x06)  # STATUS
# status flags
_STAT_DRDY = const(0x01)  # Data Ready.
_STAT_OVL = const(0x02)   # Overflow flag.
_STAT_DOR = const(0x04)   # Data skipped for reading.

# configuration
_REG_ACQ_COMMAND_1 = const(0x09)  # config mode 1
_REG_ACQ_COMMAND_2 = const(0x0a)  # config mode 2
_GAUSS_8G = const(0x10)
_GAUSS_2G = const(0x00)
_CONTI_MODE = const(0x01)
_STANDBY_MODE = const(0x00)
_ODR_10HZ = const(0x00)
_ODR_50HZ = const(0x04)
_ODR_100HZ = const(0x08)
_ODR_200HZ = const(0x0C)

_OSR_512 = const(0x00)
_OSR_256 = const(0x40)
_OSR_128 = const(0x80)
_OSR_64 = const(0xC0)
# READ REGISTER x,y,z
_AXIS_X_MSB = const(0x00)
_AXIS_X_LSB = const(0x01)
_AXIS_Y_MSB = const(0x02)
_AXIS_Y_LSB = const(0x03)
_AXIS_Z_MSB = const(0x04)
_AXIS_Z_LSB = const(0x05)

# continous with full modes: COMPASS_MODE= 0x1d
# save energy mode : COMPASS_MODE=0xC0
COMPASS_MODE = [_CONTI_MODE | _GAUSS_8G |
                _ODR_200HZ | _OSR_512, _STANDBY_MODE | _GAUSS_2G | _ODR_10HZ | _OSR_64]  # continuos mode


class Compass():
    mode = 0  # init with save energy mode
    _declination = 0.0
    _calibration = [[1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0]]

    def __init__(self, bus_num):
        try:
            self.bus = smbus.SMBus(bus_num)
            time.sleep(0.5)
            self.config(COMPASS_MODE[self.mode])
            time.sleep(0.5)
        except:
            raise RuntimeError(
                "Not found Address in I2c bus {}".format(bus_num))

    def config(self, config):
        """set compass measurement mode"""
        self._write_byte_data(_REG_ACQ_COMMAND_2, 0x80)
        self._write_byte_data(_REG_ACQ_COMMAND_2, 0x01)
        self._write_byte_data(_CMD_RESET, 0x01)
        self._write_byte_data(_REG_ACQ_COMMAND_1, config)

    def _write_byte_data(self, reg, value):
        self.bus.write_byte_data(_ADDR, reg, value)
        time.sleep(0.01)

    def switch_mode(self, mode):
        if mode == 'continuous':
            self.config(0)
        elif mode == 'standby':
            self.config(1)

    @property
    def check_status(self):
        """check status of the compass"""
        self.stt = self.bus.read_byte_data(_ADDR, _STATUS)
        return self.stt

    def read_convert(self, reg):
        """read and calculate 2 complement of 2 bytes value"""
        low = self.bus.read_byte_data(_ADDR, reg)
        high = self.bus.read_byte_data(_ADDR, reg+1)
        val = (high << 8) | low
        if (val & (1 << 16 - 1)):
            val = val - (1 << 16)
        print(val)
        return val

    def get_axes(self):
        """read x y z"""
        [x, y, z] = [None, None, None]
        i = 0
        while i < 20:
            status = self.check_status
            print(" heiiiii {}".format(status))
            if status & _STAT_OVL:
                logging.warning("overflow")
            if status & _STAT_DOR:
                # partially read
                x = self.read_byte_data(_ADDR, _AXIS_X_LSB)
                y = self.read_byte_data(_ADDR, _AXIS_Y_LSB)
                z = self.read_byte_data(_ADDR, _AXIS_Z_LSB)
                continue
            if status & _STAT_DRDY:
                # Data is ready to read.
                x = self.read_byte_data(_ADDR, _AXIS_X_LSB)
                y = self.read_byte_data(_ADDR, _AXIS_Y_LSB)
                z = self.read_byte_data(_ADDR, _AXIS_Z_LSB)
                break
            else:
                # Waiting for DRDY.
                time.sleep(0.01)
                i += 1
        return [x, y, z]

    @property
    def read_compass(self):
        """"""
        [x, y, z] = self.get_axes()
        global x1, y1
        x1 = None
        y1 = None
        if x is None or y is None:
            return None
        else:
            c = self._calibration
            x1 = x * c[0][0] + y * c[0][1] + c[0][2]
            y1 = x * c[1][0] + y * c[1][1] + c[1][2]

        angle = math.degrees(math.atan2(y1, x1))
        if angle < 0:
            angle += 360
        angle += self._declination
        if angle < 0.0:
            angle += 360.0
        elif angle >= 360.0:
            angle -= 360.0
        return angle

    def set_declination(self, value=9.76):
        """Set the magnetic declination, in degrees."""
        # tampere =+9.76
        # helsinki=+8.60
        try:
            d = float(value)
            if d < -180.0 or d > 180.0:
                logging.error(u'Declination must be >= -180 and <= 180.')
            else:
                self._declination = d
        except:
            logging.error(u'Declination must be a float value.')

    def get_declination(self):
        """Return the current set value of magnetic declination."""
        return self._declination


if __name__ == "__main__":
    compass = Compass(4)
    compass.set_declination()

    while True:
        print(compass.get_axes())
        # sys.stdout.write(compass.read_compass
        #                  )
        # sys.stdout.flush()
        time.sleep(0.5)
