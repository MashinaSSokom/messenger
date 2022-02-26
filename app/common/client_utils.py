import time
import logging

from .variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from ..logs import config_client_log

logger = logging.getLogger('client_logger')


def create_presence(account_name='Guest'):
    presence = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {ACCOUNT_NAME: account_name}
    }
    logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return presence


def process_response(response):
    logger.debug(f'Разбор ответа от сервера: {response}')
    if RESPONSE in response:
        if response[RESPONSE] == 200:
            return f'200: OK'
        return f'400: {response[ERROR]}'
    raise ValueError
