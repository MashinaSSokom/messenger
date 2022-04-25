import logging
from socket import socket
import time

from .logger import log
from .variables import USER, ACTION, ACCOUNT_NAME, RESPONSE, ERROR, TIME, PRESENCE, MESSAGE, MESSAGE_TEXT, \
    DESTINATION, SENDER, EXIT, RESPONSE_200, RESPONSE_400, GET_HISTORY, GET_USERS, GET_ACTIVE_USERS, TARGET
from .utils import send_message
from server_database import Storage
# from ..logs import config_client_log

logger = logging.getLogger('server_logger')


@log
def create_confirm_exit_message(client_name):
    message = {
        ACTION: EXIT,
        TIME: time.time(),
        SENDER: client_name,
    }
    logger.debug(f'Пользователь {client_name} вышел из системы!')
    return message


@log
def process_client_message(message: dict, client: socket, messages: list, clients: list, client_names: dict, database: Storage):
    """"""
    logger.debug(f'Обработка сообщения от клиента : {message}')

    # Checking compliance with JIM
    sorted_message_keys = sorted(list(message.keys()))
    sorted_keys1 = sorted([USER, ACTION, TIME, SENDER])
    sorted_keys2 = sorted([USER, ACTION, TIME, MESSAGE_TEXT, DESTINATION, SENDER])
    if message[SENDER] and message[ACTION] and message[TIME] and message[SENDER]:
        if message[ACTION] == PRESENCE:
            if message[SENDER] not in client_names.keys():
                client_names[message[SENDER]] = client
                client_ip_address, client_port = client.getpeername()
                database.login_user(message[SENDER], client_ip_address, client_port)
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято!'
                send_message(client, response)
                clients.remove(client)
                client.close()
            return
        elif message[ACTION] == MESSAGE and MESSAGE_TEXT in message and DESTINATION in message:
            messages.append(message)
            return
        elif message[ACTION] == GET_USERS:
            users = database.get_all_users()
            response = {
                ACTION: GET_USERS,
                MESSAGE_TEXT: ''
            }
            for user in users:
                response[MESSAGE_TEXT] += f'Пользователь: {user.username} (последний логин - {user.last_login})\n'
            send_message(client, response)
            return
        elif message[ACTION] == GET_ACTIVE_USERS:
            users = database.get_all_active_users()
            response = {
                ACTION: GET_USERS,
                MESSAGE_TEXT: ''
            }
            for user in users:
                response[MESSAGE_TEXT] += f'Пользователь: имя - {user.username}, ip - {user.ip_address}:{user.port} (время логина - {user.login_time})\n'
            send_message(client, response)
            return
        elif message[ACTION] == GET_HISTORY:
            # if MESSAGE[TARGET]:
            response = {
                ACTION: GET_HISTORY,
                MESSAGE_TEXT: ''
            }
            history = database.get_login_history(message[TARGET])
            for row in history:
                response[MESSAGE_TEXT] += f'Пользователь -{row[0]}, ip - {row[1]}:{row[2]}, последний логин - {row[3]}\n'
            send_message(client, response)
            return
        elif message[ACTION] == EXIT:
            database.logout_user(message[SENDER])
            clients.remove(client)
            del client_names[message[SENDER]]
            send_message(client, create_confirm_exit_message(message[SENDER]))
            client.close()
            return
    send_message(client, RESPONSE_400)
    return


@log
def process_sending_message(message: dict, clients: list[socket], client_names: dict):
    """"""

    if message[DESTINATION] in client_names and client_names[message[DESTINATION]] in clients:
        send_message(client_names[message[DESTINATION]], message)
        logger.debug(f'Пользователь {message[SENDER]} отправил сообщение пользователю {message[DESTINATION]}')
    elif message[DESTINATION] in client_names and client_names[message[DESTINATION]] not in clients:
        raise ConnectionError
    else:
        logger.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')
        response = RESPONSE_400
        response[ERROR] = f'Пользователль {message[DESTINATION]}  не зарегистрирован на сервере!'
        send_message(client_names[message[SENDER]], response)
