from functools import wraps, update_wrapper


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
        def func_wrapper():
            count = times
            while count > 0:
                func()
                count -= 1
        return func_wrapper
    return num_wrapper


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
