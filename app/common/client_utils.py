import time
import logging
import sys

from .logger import log
from .variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT

# from ..logs import config_client_log

logger = logging.getLogger('client_logger')


@log
def create_presence(account_name='Guest'):
    presence = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {ACCOUNT_NAME: account_name}
    }
    logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return presence


@log
def process_response(response):
    logger.debug(f'Разбор ответа от сервера: {response}')
    if RESPONSE in response:
        if response[RESPONSE] == 200:
            return f'200: OK'
        return f'400: {response[ERROR]}'
    raise ValueError


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной комманды
    """
    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        sock.close()
        logger.info('Завершение работы по команде пользователя.')
        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        USER: {ACCOUNT_NAME: account_name},
        MESSAGE_TEXT: message
    }
    logger.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


@log
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            USER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[USER][ACCOUNT_NAME]}:\n{message[MESSAGE_TEXT]}')
        logger.info(f'Получено сообщение от пользователя '
                    f'{message[USER]}:\n{message[MESSAGE_TEXT]}')
    else:
        logger.error(f'Получено некорректное сообщение с сервера: {message}')
