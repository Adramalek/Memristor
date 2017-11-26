from serial import Serial
from utils import positive


class Comp(object):
    def __init__(self, name, baudrate=115200, cr='\r', lf='\n'):
        self.ser = Serial(name)  # open serial port
        self.ser.baudrate = baudrate
        if self.ser.name != name:
            raise ValueError()
        self.cr = cr.encode('ascii')
        self.lf = lf.encode('ascii')
        self.crlf = cr + lf

    def close(self):
        self.ser.close()

    # start experiment
    def _start(self):
        self.ser.write("nstart\r".encode('ascii'))
        ans = "Time=120".encode('ascii')
        line = self.ser.readline()
        while not (ans in line):
            print(line)
            line = self.ser.read_until(self.crlf, 20)
        print(line)
        return 0

    def _end_pulse(self):
        ans = "DONE".encode('ascii')
        line = ''
        while not (ans in line):
            print(line)
            line = self.ser.read_until(self.crlf, 20)
        print(line)
        return 0

    def experiment(self):
        if self._start() == 0:
            if self._end_pulse() == 0:
                return 0
        return 1

    # set width of high level ms
    @positive(is_method=True)
    def set_high_del(self, delay):
        cmd = ("psetpl " + str(delay) + "\r").encode('ascii')
        ans = ("Set_Pulse=" + str(delay)).encode('ascii')
        self.ser.write(cmd)
        line = self.ser.read_until(self.crlf, 20)
        print(line)
        if ans in line:
            return 0
        else:
            return 1

    # set width of low level ms
    @positive(is_method=True)
    def set_low_del(self, delay):
        cmd = ("psetpdl " + str(delay) + "\r").encode('ascii')
        ans = ("Set_Pulse_Delay=" + str(delay)).encode('ascii')
        self.ser.write(cmd)
        line = self.ser.read_until(self.crlf, 20)
        print(line)
        if ans in line:
            return 0
        else:
            return 1
