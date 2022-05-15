from logging import exception
import simpleaudio as sa
import time
import threading

import os
import sys

curr_folder = os.path.dirname(os.path.realpath(__file__))


class Speaker(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(Speaker, self).__init__(*args, *kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()
        # pygame.mixer.init()

    # def __init__(self):
        # pygame.mixer.init()
        # print(self.obj)
        #self.events = {}
    # def run(self):

    def playbackThread(self, command):

        if command == 0:
            t1 = threading.Thread(target=self.blue)
        elif command == 1:
            t1 = threading.Thread(target=self.green)
        elif command == 2:
            t1 = threading.Thread(target=self.red)
        elif command == 3:
            t1 = threading.Thread(target=self.grabbed)
        elif command == 4:
            t1 = threading.Thread(target=self.released)
        elif command == 5:
            t1 = threading.Thread(target=self.scored)
        t1.start()



    def killPlaybackThread(self):
        ''''''

    def blue(self, file=curr_folder+"/mp3/blue.wav"):
        self.stop()
        try:
            wave_obj = sa.WaveObject.from_wave_file(file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            while play_obj.is_playing() == True:
                continue
        except Exception:
            pass

    
    def green(self, file=curr_folder+"/mp3/green.wav"):
        self.stop()
        try:
            wave_obj = sa.WaveObject.from_wave_file(file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            while play_obj.is_playing() == True:
                continue
        except Exception:
            pass

    def red(self, file=curr_folder+"/mp3/red.wav"):
        self.stop()
        try:
            wave_obj = sa.WaveObject.from_wave_file(file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            while play_obj.is_playing() == True:
                continue
        except Exception:
            pass




    def forward(self, file=curr_folder+"/mp3/forward.wav"):
        self.stop()
        wave_obj = sa.WaveObject.from_wave_file(file)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        while play_obj.is_playing() == True:
            continue

    def next(self, file=curr_folder+"/mp3/next.wav"):
        self.stop()
        try:
            wave_obj = sa.WaveObject.from_wave_file(file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            while play_obj.is_playing() == True:
                continue
        except Exception:
            pass

    def back(self, file=curr_folder+"/mp3/back.wav"):
        self.stop()
        try:
            wave_obj = sa.WaveObject.from_wave_file(file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            while play_obj.is_playing() == True:
                continue
        except Exception:
            pass

    def grabbed(self, file=curr_folder+"/mp3/grabbed-ball.wav"):
        try:
            self.stop()
            wave_obj = sa.WaveObject.from_wave_file(file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            while play_obj.is_playing() == True:
                continue
        except Exception:
            pass

    def released(self, file=curr_folder+"/mp3/put-in-box.wav"):
        try:
            self.stop()
            wave_obj = sa.WaveObject.from_wave_file(file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            while play_obj.is_playing() == True:
                continue
        except Exception:
            pass

    def scored(self, file=curr_folder+"/mp3/score.wav"):
        try:
            self.stop()
            wave_obj = sa.WaveObject.from_wave_file(file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            while play_obj.is_playing() == True:
                continue
        except Exception:
            pass

    def released(self, file=curr_folder+"/mp3/put-in-box.wav"):
        try:
            self.stop()
            wave_obj = sa.WaveObject.from_wave_file(file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            while play_obj.is_playing() == True:
                continue
        except Exception:
            pass

    def stop(self):
        wave_obj = sa.stop_all()

    def run(self):
        while 1:
            self.__flag.wait()
            """"""

    def clear(self):
        self.__flag.clear()


if __name__ == "__main__":
    speaker = Speaker()
    speaker.start()
    speaker.playbackThread("forward")
    time.sleep(1)
    speaker.playbackThread("back")
    time.sleep(2)
    speaker.playbackThread("next")
    time.sleep(2)
    speaker.playbackThread("grabbed")
    time.sleep(2)
    speaker.playbackThread("released")
    time.sleep(3)
    speaker.playbackThread("scored")