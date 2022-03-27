import pygame
import time
import threading
import board


class Speaker(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(Speaker, self).__init__(*args, *kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()
        pygame.mixer.init()

    # def __init__(self):
        # pygame.mixer.init()
        # print(self.obj)
        #self.events = {}
    # def run(self):

    def playbackThread(self, command):
        if command == "back":
            t1 = threading.Thread(target=self.back)
        elif command == "forward":
            t1 = threading.Thread(target=self.forward)
        t1.start()

    def killPlaybackThread(self):
        ''''''

    def back(self, file="./voice/mp3/back.mp3"):
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

    def forward(self, file="./voice/mp3/forward.mp3"):
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

    def clear(self):
        self.events[get_ident()][0].clear()


if __name__ == "__main__":
    speaker = Speaker()
    speaker.start()
    speaker.playbackThread("forward")
    # speaker.__init__()
    # speaker.back()
    # speaker.forward()
