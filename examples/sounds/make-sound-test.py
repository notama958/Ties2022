import threading
import pygame
import digitalio
import board
import time
# initial configuration
# you have to turn the bluetooth on ( check with vnc and try to connect it with the speaker device)
# or you can run commands on bash to config/connect
# see this link to https://howchoo.com/pi/bluetooth-raspberry-pi
# Then run the code below to see how it works
# note down the bluetooth MAC also

# btw the sound might sound not smooth the tip is
# echo "power off" | bluetoothctl
# systemctl daemon-reload
# systemctl restart bluetooth
# the MAC address depend on NEXON speaker change if it different
# echo  "power on"|bluetoothctl
# echo  "connect 78:B6:6A:3B:F0:6C"|bluetoothctl
# echo  "quit"|bluetoothctl
# It's now working smoothly ^^


# you can remove this led and keep the pygame code only to see how the bluetooth speaker works
led = digitalio.DigitalInOut(board.D4)
led.direction = digitalio.Direction.OUTPUT


def make_sound(file="song.mp3"):
    """"""
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue


def blink_sound():
    """"""
    while True:
        led.value = True
        make_sound()
        led.value = False
        time.sleep(0.5)

# class Speaker(threading.Thead):
#     def __init__(self):
#         """"""
#     def getVoice(self, file):
#         """ play the mp3 """

# class Face(threading.Thread):
# android phone

# speaker= Speaker()


if __name__ == "__main__":
    pygame.mixer.init()
    blink_sound()
