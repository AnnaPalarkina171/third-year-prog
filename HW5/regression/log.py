import logging


def get_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    log.addHandler(handler)
    return log
