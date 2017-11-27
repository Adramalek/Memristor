from functools import wraps, update_wrapper
from threading import Thread, Event
from os import remove
from os.path import exists
from time import sleep
import logging


def init_log(file_name):
    if exists(file_name):
        remove(file_name)
    logging.basicConfig(filename=file_name, level=logging.INFO, format='[%(asctime)s]%(levelname)s:%(message)s')


def _assert_all_positive(*args):
    for arg in args:
        if arg <= 0:
                raise ValueError('Arguments should be positive')


def positive(is_method=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lst = args[1:] if is_method else args
            _assert_all_positive(*lst)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def iterable_equal(iter1, iter2):
    if len(iter1) == len(iter2):
        for o1, o2 in zip(iter1, iter2):
            if o1 != o2:
                return False
        return True
    return False


def loops(times):
    def num_wrapper(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            count = times
            while count > 0:
                func(*args, **kwargs)
                count -= 1
        return func_wrapper
    return num_wrapper


def waiter(start_message, end_message):
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            def wait(event):
                print(start_message)
                max_count = 100
                count = 0
                while not event.is_set():
                    if count < max_count:
                        print('#', end='')
                        count += 1
                    else:
                        print()
                        count = 0
                    sleep(1)
                print()
                print(end_message)
            stop_event = Event()
            thread = Thread(target=wait, args=(stop_event,))
            thread.start()
            res = func(*args, **kwargs)
            stop_event.set()
            thread.join()
            return res
        return func_wrapper
    return decorator


def overload(func):
    registry = {}

    def dispatch(*args_clss):
        for key in registry:
            if iterable_equal(args_clss, key):
                return registry[key]

    def register(*args_clss, func=None):
        if func is None:
            return lambda f: register(*args_clss, func=f)
        registry[args_clss] = func
        return func

    def wrapper(*args, **kwargs):
        _args = args[1:]
        if _args:
            return dispatch(*tuple(arg.__class__ for arg in _args))(*args, **kwargs)
        else:
            return registry[()](*args, **kwargs)
    registry[()] = func
    wrapper.register = register
    update_wrapper(wrapper, func)
    return wrapper


# decorator
def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate
