import json
import socket
import time
import logging
import sys
import threading

from client_database import ClientStorage
from .logger import log
from .variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, EXIT, SENDER, \
    DESTINATION, GET_USERS, GET_ACTIVE_USERS, GET_HISTORY, TARGET, ADD_CONTACT, DEL_CONTACT, GET_MESSAGE_HISTORY, \
    GET_CONTACTS
from .utils import get_message, send_message
from .errors import IncorrectDataRecivedError, ServerError

# from ..logs import config_client_log

logger = logging.getLogger('client_logger')

sock_lock = threading.Lock()
database_lock = threading.Lock()

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
    logger.debug(f'Сформировано {GET_USERS} сообщение для пользователя {client_name}')
    return message


@log
def create_get_active_users_message(client_name):
    message = {
        ACTION: GET_ACTIVE_USERS,
        TIME: time.time(),
        SENDER: client_name,
        USER: {ACCOUNT_NAME: client_name}
    }
    logger.debug(f'Сформировано {GET_ACTIVE_USERS} сообщение для пользователя {client_name}')
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
    logger.debug(f'Сформировано {GET_HISTORY} сообщение для пользователя {client_name}')
    return message

@log
def create_add_contact_message(client_name, contact_name):
    message = {
        ACTION: ADD_CONTACT,
        TARGET: contact_name,
        TIME: time.time(),
        SENDER: client_name,
        USER: {ACCOUNT_NAME: client_name}
    }
    logger.debug(f'Сформировано {ADD_CONTACT} сообщение для пользователя {client_name}')
    return message

@log
def create_del_contact_message(client_name, contact_name):
    message = {
        ACTION: DEL_CONTACT,
        TARGET: contact_name,
        TIME: time.time(),
        SENDER: client_name,
        USER: {ACCOUNT_NAME: client_name}
    }
    logger.debug(f'Сформировано {DEL_CONTACT} сообщение для пользователя {client_name}')
    return message

@log
def create_get_contacts_message(client_name):
    message = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        SENDER: client_name,
        USER: {ACCOUNT_NAME: client_name}
    }
    logger.debug(f'Сформировано {GET_CONTACTS} сообщение для пользователя {client_name}')
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
def create_message(sock, client_name: str, database: ClientStorage):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной комманды
    """
    destination = input('Введите имя получателя: ')
    message = input('Введите сообщение: ')
    with database_lock:
        if not database.check_is_known_user(destination):
            print(f'Попытка отправить сообщение неизвастному пользователю :(')
            return

    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        USER: {ACCOUNT_NAME: client_name},
        SENDER: client_name,
        DESTINATION: destination,
        MESSAGE_TEXT: message
    }
    logger.debug(f'Пользователем {client_name} сформирован словарь сообщения: {message_dict}')
    #TODO: сохранять сообщения для пользователей не в сети, чтобы они не потерялись
    with database_lock:
        database.save_message(client_name, destination, message)
    return message_dict


@log
def receive_message_from_server(client_socket: socket.socket, client_name: str, database: ClientStorage):
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
                if message[RESPONSE] == 200:
                    if message[ACTION] == GET_USERS:
                        print(f'\nСписок всех пользователей:\n{message[MESSAGE_TEXT]}')
                    elif message[ACTION] == GET_ACTIVE_USERS:
                        print(f'\nСписок всех активных пользователей:\n{message[MESSAGE_TEXT]}')
                    elif message[ACTION] == GET_HISTORY:
                        print(f'\nНайденная история (последние 10 записей):\n{message[MESSAGE_TEXT]}')
                    elif message[ACTION] == ADD_CONTACT:
                        with database_lock:
                            database.add_contact(message[TARGET])
                            print(f'\nПользователль {message[TARGET]} добавлен в список контактов!')
                    elif message[ACTION] == DEL_CONTACT:
                        with database_lock:
                            database.del_contact(message[TARGET])
                            print(f'\nПользователль {message[TARGET]} удален из списка контактов!')
                    elif message[ACTION] == GET_CONTACTS:
                        print(f'\nСписок контактов:\n{message[MESSAGE_TEXT]}')
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
def user_interface(client_socket: socket.socket, client_name: str, database: ClientStorage) -> None:
    print_user_hint()
    while True:
        command = input(f'Введите команду (подсказка - help): ')
        if command == MESSAGE:
            message = create_message(client_socket, client_name, database)
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
        elif command == ADD_CONTACT:
            contact_name = input('Введите имя пользователя для добавления в контакты: ')
            with database_lock:
                if database.check_is_contact(contact_name):
                    print(f'Попытка добавления существующего контакта!')
                else:
                    if database.check_is_known_user(contact_name):
                        send_message(client_socket, create_add_contact_message(client_name, contact_name))
                    else:
                        print(f'Попытка добавления неизвестного пользователя!')
        elif command == DEL_CONTACT:
            contact_name = input('Введите имя пользователя для удаления из контактов: ')
            with database_lock:
                if not database.check_is_contact(contact_name):
                    print(f'Попытка удаления несуществующего контакта!')
                else:
                    send_message(client_socket, create_del_contact_message(client_name, contact_name))
        elif command == GET_CONTACTS:
            send_message(client_socket, create_get_contacts_message(client_name))
        elif command == GET_MESSAGE_HISTORY: #TODO: доделать получение истории сообщений
            pass
        elif command == 'help':
            print_user_hint()
        else:
            print('Некорректный ввод, попробойте снова... Чтобы получить подсказку, используется команду help.\n')


@log
def load_users_from_server(client_socket: socket.socket, client_name: str, database: ClientStorage):
    send_message(client_socket, create_get_users_message(client_name))
    response = get_message(client_socket)
    logger.info(f'Клиент {client_name} получил от сервера сообщение {response}')
    result = process_response(response)
    if result == f'200: OK':
        return response[MESSAGE_TEXT]
    raise ServerError(response[ERROR])
#TODO: исправить дублирование SENDER и USER (оставить SENDER)
