import logging
from logging.handlers import RotatingFileHandler

from utils.config import config


def init_logger():
    log_file = config.get('logger', 'file')

    handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
    formatter = logging.Formatter(
        '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    level = config.get('logger', 'level')
    logging_level = logging.INFO
    if level is 'info':
        logging_level = logging.INFO
    elif level is 'debug':
        logging_level = logging.DEBUG
    elif level is 'error':
        logging_level = logging.ERROR

    handler.setLevel(logging_level)
    return handler


handler = init_logger()
