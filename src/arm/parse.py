
import sys
import os


def parse():
    f = open("config.txt", "r")
    lines = f.readlines()
    new_arr = [0]*16
    for line in lines:
        line = line.strip()
        if line.isdigit():
            """"""
            new_arr[int(line)] += 1
    return new_arr


# # print(parse())
# for i in parse():
#     print(i)
