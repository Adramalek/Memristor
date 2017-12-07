from serial import Serial
from utils import positive_args, timer
import logging


class COMPortController(object):
    def __init__(self, name, baudrate=115200, cr='\r', lf='\n', timeout=None, tries=10):
        self.ser = Serial(name, timeout=timeout)  # open serial port
        self.ser.baudrate = baudrate
        if self.ser.name != name:
            raise ValueError()
        self.cr = cr.encode('ascii')
        self.lf = lf.encode('ascii')
        self.crlf = cr + lf
        logging.info('Open port {}'.format(name))

    @property
    def timeout(self):
        return self.ser.timeout

    @timeout.setter
    def timeout(self, timeout):
        self.ser.timeout = timeout

    def close(self):
        self.ser.close()
        logging.info('Close port')

    # start experiment
    @timer
    def start(self):
        logging.info('Start pulsing')
        self.ser.write("nstart\r".encode('ascii'))
        ans = "Time=".encode('ascii')
        line = self.ser.read_until(self.cr, 30)
        while not (ans in line):
            line = self.ser.read_until(self.cr, 30)
        logging.info(line.decode().replace('\n', '').replace('\r', ''))
        logging.info('Finished')
        return 0

    @timer
    def reset(self):
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
            if self.reset() == 0:
                return 0
        return 1

    def _send(self, cmd, ans):
        logging.info(cmd.decode().replace('\n', '').replace('\r', ''))
        self.ser.write(cmd)
        line = self.ser.read_until(self.cr, 30)
        logging.info(line.decode().replace('\n', '').replace('\r', ''))
        if ans in line:
            return 0
        else:
            return 1

    @positive_args(is_method=True)
    def set_time(self, time):
        cmd = "psettm {}\r".format(time).encode('ascii')
        ans = "Exp_time={}".format(time).encode('ascii')
        self._send(cmd, ans)

    @positive_args
    def set_reset(self, time):
        cmd = 'psetrtm {}\r'.format(time).encode('ascii')
        ans = "Reset_time={}".format(time).encode('ascii')
        self._send(cmd, ans)

    # set width of high level ms
    @positive_args(is_method=True)
    def set_high_del(self, delay):
        cmd = "psetpl {}\r".format(delay).encode('ascii')
        ans = "Set_Pulse={}".format(delay).encode('ascii')
        self._send(cmd, ans)

    # set width of low level ms
    @positive_args(is_method=True)
    def set_low_del(self, delay):
        cmd = "psetpdl {}\r".format(delay).encode('ascii')
        ans = "Set_Pulse_Delay={}".format(delay).encode('ascii')
        self._send(cmd, ans)

    @positive_args(is_method=True)
    def set_duty(self, duty):
        cmd = "psetdt {}\r".format(duty).encode('ascii')
        ans = "Set_Duty={}".format(duty).encode('ascii')
        self._send(cmd, ans)

    @positive_args(is_method=True)
    def set_period(self, period):
        cmd = "psetp {}".format(period).encode('ascii')
        ans = "Set_Period={}".format(period).encode('ascii')
        self._send(cmd, ans)
