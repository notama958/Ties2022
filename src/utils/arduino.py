from threading import Timer
import serial
import threading
import time
TTY = '/dev/ttyACM1'

CMDS = {
    'BLUE': b'0\n',
    'GREEN': b'1\n',
    'RED': b'2\n',
    'WHITE': b'3\n',
    'SOLENOID': b'4\n',
    'STOP': b'5\n'
}


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class ArduinoControl(threading.Thread):
    read = True

    def __init__(self, *args, **kwargs):
        self.ser = serial.Serial(TTY, 9600, timeout=1)
        self.ser.reset_input_buffer()
        self.solenoid = RepeatedTimer(
            1, self.runSolenoid)  # run solenoid repeatedly
        super(ArduinoControl, self).__init__(*args, *kwargs)
        self.__flag = threading.Event()
        self.__flag.set()

        # self.resume()

    def runSolenoid(self):
        self.ser.write(CMDS.get('SOLENOID'))

    def runLed(self, led):
        if CMDS.get(led):
            self.ser.write(CMDS.get(led))

    def readCommand(self):
        # self.resume()
        line = self.ser.readline().decode('utf-8').rstrip()
        print(line)
        time.sleep(1)

    def run(self):
        while self.read:
            self.__flag.wait()
            self.readCommand()
            pass

    def pause(self):
        self.__flag.clear()
        # self.read = False

    def resume(self):
        print("resume")
        self.__flag.set()
        self.read = True

    def stop(self):
        self.pause()
        self.ser.write(CMDS.get('STOP'))


if __name__ == '__main__':
    slave = ArduinoControl()
    slave.start()
    time.sleep(5)
    slave.pause()
    time.sleep(1)
    slave.resume()

    # slave.readCommand()
