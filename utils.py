def frange(_min, _max, step=1.0):
    while _min < _max:
        yield _min
        _min += step


def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate
