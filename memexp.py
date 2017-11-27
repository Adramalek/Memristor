import cv2
import argparse
from comm import Comp
from threading import Thread, Event
from os import remove, mkdir
from os.path import join, exists
from utils import init_log, positive
import logging


class Viwriter(object):
    def __init__(self, stopper=None, path='meas', flip=False):
        super().__init__()
        if not exists(path):
            mkdir(path)
        self.path = path
        self._cam = cv2.VideoCapture(0)
        self._flip = flip
        w = self._cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self._cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self._size = (int(w), int(h))
        self._fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self._stopper = stopper if stopper else Event()
        self._out = None
        self._file = None
        self._blocked = Event()
        self.thread = None

    def _block(func):
        def magic(self, *args, **kwargs):
            if not self._blocked.is_set():
                self._blocked.set()
                return func(self, *args, **kwargs)
            else:
                return None
        return magic

    # @_block
    # def start(self):
    #     print('started')
    #     super().start()
    #
    # @start.register(str)
    @_block
    def start(self, file_name):
        self._stopper.clear()
        self._file = join(self.path, file_name+'.mp4')
        if exists(self._file):
            remove(self._file)

        def _run(self):
            logging.info('Start recording into {}'.format(self._file))
            self._out = cv2.VideoWriter(self._file, self._fourcc, 20.0, self._size)
            while self._cam.isOpened() and not self._stopper.is_set():
                ret, frame = self._cam.read()
                if not ret:
                    break
                if self._flip:
                    frame = cv2.flip(frame, -1)
                # cv2.imshow('vicap', frame)
                self._out.write(frame)
            self._out.release()
            self._out = None
            # cv2.destroyAllWindows()
            self._blocked.clear()
            logging.info('Stop recording')

        self.thread = Thread(target=_run, args=(self,))
        self.thread.start()

    def stop(self):
        self._stopper.set()
        self.thread.join()

    @_block
    def release(self):
        self._cam.release()


def experiment(port_name, dir_path, initial_high=10, initial_low=10, max_period=10000, high_step=10, low_step=10):
    comp = Comp(port_name)
    viwriter = Viwriter(path=dir_path)
    high = initial_high
    period = high+initial_low
    low = period-high
    while period <= max_period:
        while low > 0:
            comp.timeout = 5
            comp.set_high_del(high)
            comp.set_low_del(low)
            logging.info("Run H{} L{}".format(high, low))
            comp.timeout = None
            viwriter.start('P{}H{}'.format(period, high))
            comp.start()
            viwriter.stop()
            comp.end_pulse()
            high += high_step
            low = period-high
        high = initial_high
        period += low_step
        low = period - high

    viwriter.release()
    comp.close()


def init_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str)
    parser.add_argument('-D', '--storage_path', type=str, metavar='dir', nargs='?', default='meas')
    parser.add_argument('-H', '--init_high', type=int, metavar='ms', nargs='?', default=10)
    parser.add_argument('-L', '--init_low', type=int, metavar='ms', nargs='?', default=10)
    parser.add_argument('-P', '--max_period', type=int, metavar='ms', nargs='?', default=10000)
    parser.add_argument('-sh', '--step_high', type=int, metavar='ms', nargs='?', default=10)
    parser.add_argument('-sl', '--step_low', type=int, metavar='ms', nargs='?', default=10)
    parser.add_argument('-f', '--flip', action='store_true')

    return parser


if __name__ == '__main__':
    parser = init_argparser()
    args = parser.parse_args()

    init_log('experiment.log')
    experiment(args.port, args.storage_path, max_period=args.max_period)
