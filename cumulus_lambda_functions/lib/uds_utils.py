import backoff

class JitteredBackoffException(Exception):
    pass


@backoff.on_exception(
    backoff.expo,
    Exception,
    max_value=13,
    max_time=34,
    giveup=lambda e: isinstance(e, JitteredBackoffException),
)
def backoff_wrapper(func, *args, **kwargs):
    """
    Run a function wrapped in exponential backoff.
    :param func: function or method object
    :param args: args to pass to function
    :param kwargs: keyword args to pass to function
    :return:
    """
    return func(*args, **kwargs)