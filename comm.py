from serial import Serial
from utils import positive, waiter
import logging


class Comp(object):
    def __init__(self, name, baudrate=115200, cr='\r', lf='\n', timeout=None, tries=10):
        self.ser = Serial(name, timeout=timeout)  # open serial port
        self.ser.baudrate = baudrate
        if self.ser.name != name:
            raise ValueError()
        self.cr = cr.encode('ascii')
        self.lf = lf.encode('ascii')
        self.crlf = cr + lf

    @property
    def timeout(self):
        return self.ser.timeout

    @timeout.setter
    def timeout(self, timeout):
        self.ser.timeout = timeout

    def close(self):
        self.ser.close()

    # start experiment
    def start(self):
        logging.info('Start pulsing')
        self.ser.write("nstart\r".encode('ascii'))
        ans = "Time=120".encode('ascii')
        line = self.ser.read_until(self.cr, 30)
        while not (ans in line):
            line = self.ser.read_until(self.cr, 30)
        # print(line.decode().replace('\n', ''))
        logging.info('Finished')
        return 0

    def end_pulse(self):
        logging.info('Start resetting')
        ans = "DONE".encode('ascii')
        line = self.ser.read_until(self.cr, 30)
        while not (ans in line):
            line = self.ser.read_until(self.cr, 30)
        # print(line.decode().replace('\n', ''))
        logging.info('Finished')
        return 0

    def experiment(self):
        if self.start() == 0:
            if self.end_pulse() == 0:
                return 0
        return 1

    # set width of high level ms
    @positive(is_method=True)
    def set_high_del(self, delay):
        cmd = ("psetpl " + str(delay) + "\r").encode('ascii')
        ans = ("Set_Pulse=" + str(delay)).encode('ascii')
        logging.info(cmd.decode().replace('\n', ''))
        self.ser.write(cmd)
        line = self.ser.read_until(self.cr, 30)
        logging.info(line.decode().replace('\n', ''))
        if ans in line:
            return 0
        else:
            return 1

    # set width of low level ms
    @positive(is_method=True)
    def set_low_del(self, delay):
        cmd = ("psetpdl " + str(delay) + "\r").encode('ascii')
        ans = ("Set_Pulse_Delay=" + str(delay)).encode('ascii')
        logging.info(cmd.decode().replace('\n', ''))
        self.ser.write(cmd)
        line = self.ser.read_until(self.cr, 30)
        logging.info(line.decode().replace('\n', ''))
        if ans in line:
            return 0
        else:
            return 1
