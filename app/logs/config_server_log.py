""" SERVER LOGGER CONFIG"""
import os
import sys
import logging

from logging.handlers import TimedRotatingFileHandler

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

file_handler = TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='D')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(stream=sys.stderr)
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.ERROR)


logger = logging.getLogger('server_logger')
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
