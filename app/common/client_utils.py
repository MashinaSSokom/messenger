import json
import socket
import time
import logging
import sys

from .logger import log
from .variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, EXIT, SENDER,\
    DESTINATION, GET_USERS, GET_ACTIVE_USERS, GET_HISTORY, TARGET
from .utils import get_message, send_message
from .errors import IncorrectDataRecivedError
# from ..logs import config_client_log

logger = logging.getLogger('client_logger')


@log
def create_presence(client_name):
    presence = {
        ACTION: PRESENCE,
        TIME: time.time(),
        SENDER: client_name,
        USER: {ACCOUNT_NAME: client_name}
    }
    logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {client_name}')
    return presence


@log
def create_exit_message(client_name):
    message = {
        ACTION: EXIT,
        TIME: time.time(),
        SENDER: client_name,
        USER: {ACCOUNT_NAME: client_name}
    }
    logger.debug(f'Сформировано {EXIT} сообщение для пользователя {client_name}')
    return message


@log
def create_get_users_message(client_name):
    message = {
        ACTION: GET_USERS,
        TIME: time.time(),
        SENDER: client_name,
        USER: {ACCOUNT_NAME: client_name}
    }
    logger.debug(f'Сформировано {EXIT} сообщение для пользователя {client_name}')
    return message


@log
def create_get_active_users_message(client_name):
    message = {
        ACTION: GET_ACTIVE_USERS,
        TIME: time.time(),
        SENDER: client_name,
        USER: {ACCOUNT_NAME: client_name}
    }
    logger.debug(f'Сформировано {EXIT} сообщение для пользователя {client_name}')
    return message


@log
def create_get_history_message(client_name, target=None):
    message = {
        ACTION: GET_HISTORY,
        TARGET: target,
        TIME: time.time(),
        SENDER: client_name,
        USER: {ACCOUNT_NAME: client_name}
    }
    logger.debug(f'Сформировано {EXIT} сообщение для пользователя {client_name}')
    return message

@log
def process_response(response):
    logger.debug(f'Разбор ответа от сервера: {response}')
    if RESPONSE in response:
        if response[RESPONSE] == 200:
            return f'200: OK'
        return f'400: {response[ERROR]}'
    raise ValueError


@log
def create_message(sock, client_name):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной комманды
    """
    destination = input('Введите имя получателя: ')
    message = input('Введите сообщение: ')
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        USER: {ACCOUNT_NAME: client_name},
        SENDER: client_name,
        DESTINATION: destination,
        MESSAGE_TEXT: message
    }
    logger.debug(f'Пользователем {client_name} сформирован словарь сообщения: {message_dict}')
    return message_dict


@log
def receive_message_from_server(client_socket: socket.socket, client_name: str):
    while True:
        try:
            message = get_message(client_socket)
            sorted_message_keys = sorted(list(message.keys()))
            sorted_keys = sorted([USER, ACTION, TIME, SENDER, DESTINATION, MESSAGE_TEXT])
            if sorted_keys == sorted_message_keys:
                if message[DESTINATION] == client_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n'
                          f'{message[MESSAGE_TEXT]}\n')
                    logger.info(f'Клиент {client_name} получил сообщение от {message[SENDER]}')
            else:
                if message[ACTION] == GET_USERS:
                    print(f'\nСписок всех пользователей:\n{message[MESSAGE_TEXT]}')
                elif message[ACTION] == GET_ACTIVE_USERS:
                    print(f'\nСписок всех активных пользователей:\n{message[MESSAGE_TEXT]}')
                elif message[ACTION] == GET_HISTORY:
                    print(f'\nНайденная история (последние 10 записей):\n{message[MESSAGE_TEXT]}')
                elif message[ACTION] == EXIT:
                    print(f'\nВыход из программы завершен успешно! До свидания, {message[SENDER]} ^_^')
                    sys.exit(0)
                else:
                    print(f'Ошибка: {message[ERROR]}')
                    logger.error(f'{client_name} - получено некооректное сообщение: {message}')
            print('Введите команду (подсказка - help): ', end='')
        except IncorrectDataRecivedError:
            logger.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError) as e:
            print(f'Потеряно соединение с сервером :( \n '
                  f'Выход из программы...')
            logger.critical(f'{client_name} - потеряно соединение с сервером! Ошибка: {e}')
            time.sleep(1)
            break


def print_user_hint():
    print(f'Поддерживаемые команды: \n'
          f'message - отправить сообщение (получатель и текст сообщения будут запрошены отдельно)\n'
          f'get_users - получение списка всех пользователей\n'
          f'get_active_users - получение списка всех активных пользователей\n'
          f'get_history - получение последних 10 записей истории (пользователь будет запрошен отдельно)\n'
          f'help - показать подсказку\n'
          f'exit - выйти из программы\n')


@log
def user_interface(client_socket: socket.socket, client_name: str):
    print_user_hint()
    while True:
        command = input(f'Введите команду (подсказка - help): ')
        if command == MESSAGE:
            message = create_message(client_socket, client_name)
            send_message(client_socket, message)
        elif command == EXIT:
            send_message(client_socket, create_exit_message(client_name))
            print(f'Выход из программы...')
            logger.info(f'Клиент {client_name} вышел из программы')
            time.sleep(1)
            break
        elif command == GET_USERS:
            send_message(client_socket, create_get_users_message(client_name))
        elif command == GET_ACTIVE_USERS:
            send_message(client_socket, create_get_active_users_message(client_name))
        elif command == GET_HISTORY:
            user_name = input(f'Введите имя пользователя для поиска (либо оставьте поле пустым для получения последних 50 записей): ')
            if not client_name:
                user_name = None
            send_message(client_socket, create_get_history_message(client_name, target=user_name))
        elif command == 'help':
            print_user_hint()
        else:
            print('Некорректный ввод, попробойте снова... Чтобы получить подсказку, используется команду help.\n')




#TODO: исправить дублирование SENDER и USER (оставить SENDER)