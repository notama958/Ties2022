import smbus
import time

addr = 0x60
bus = smbus.SMBus(4)
time.sleep(1)
while 1:
    # low precision
    # val = bus.read_byte_data(addr, 0x01)
    # bearing = val*360/255
    # print(bearing)
    # high precision
    high = bus.read_byte_data(addr, 0x02)
    low = bus.read_byte_data(addr, 0x03)
    bearing = ((high << 8) | low)
    # print(bearing)
    degree = bearing*360/3599
    print(degree)
    time.sleep(0.4)
