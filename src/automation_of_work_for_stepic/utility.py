import functools

def singleton(cls):
    """
    Паттерн реализующий паттерн одиночка
    :param cls:
    :return:
    """
    instance=None

    @functools.wraps(cls)
    def inner(*args,**kwargs):
        nonlocal instance
        if instance is None:
            instance=cls(*args,**kwargs)
        return instance
    return inner
