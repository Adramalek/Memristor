import cv2
from threading import Thread, Event
from os import remove, mkdir
from os.path import join, exists
import logging

__all__ = ['Viwriter',
           'write_voltage',
           'stop_writing']


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


def write_voltage(path, high_time, low_time, stopper, step=10e-4, high_val=1, low_val=0):
    def func(stopper):
        with open(path, 'w') as result:
            common_time = 0
            high = True
            time = high_time
            while not stopper.is_set():
                if high:
                    val = high_val
                    pass
                else:
                    val = low_val
                    pass
                result.write('{},{}'.format(common_time, val))
                common_time += step
                time -= step
                if time <= 0:
                    high = not high
                    time = high_time if high else low_time
    thread = Thread(target=func, args=(stopper,))
    thread.start()


def stop_writing(stopper):
    stopper.set()
