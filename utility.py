import logging


class Logging(object):
    def __init__(self, *args, **kwargs):
        logging.basicConfig(format='%(asctime)s   %(levelname)s: %(message)s', datefmt='%d-%m-%y  %H:%M:%S',
                            level=logging.DEBUG)

    @staticmethod
    def info(message):
        logging.info(message)

    @staticmethod
    def debug(message):
        logging.debug(message)

    @staticmethod
    def warning(message):
        logging.warning(message)

    @staticmethod
    def error(message):
        logging.error(message)

    @staticmethod
    def critical(message):
        logging.critical(message)
