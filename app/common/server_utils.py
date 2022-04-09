import logging
from socket import socket

from .logger import log
from .variables import USER, ACTION, ACCOUNT_NAME, RESPONSE, ERROR, TIME, PRESENCE, MESSAGE, MESSAGE_TEXT, \
    DESTINATION, SENDER, EXIT, RESPONSE_200, RESPONSE_400
from .utils import send_message

# from ..logs import config_client_log

logger = logging.getLogger('server_logger')


@log
def process_client_message(message: dict, client: socket, messages: list, clients: list, client_names: dict):
    """"""
    logger.debug(f'Обработка сообщения от клиента : {message}')

    # Checking compliance with JIM
    sorted_message_keys = sorted(list(message.keys()))
    sorted_keys1 = sorted([USER, ACTION, TIME])
    sorted_keys2 = sorted([USER, ACTION, TIME, MESSAGE_TEXT])
    if (sorted_keys1 == sorted_message_keys or sorted_keys2 == sorted_message_keys) and message[USER][ACCOUNT_NAME] \
            and message[TIME]:
        if message[ACTION] == PRESENCE:
            if message[USER][ACCOUNT_NAME] not in client_names.keys():
                send_message(client, RESPONSE_200)
                client_names[message[USER][ACCOUNT_NAME]] = client
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято!'
                send_message(client, response)
                clients.remove(client)
                client.close()
            return
        elif message[ACTION] == MESSAGE and MESSAGE_TEXT in message and DESTINATION in message and SENDER in message:
            messages.append((message[USER][ACCOUNT_NAME], message[MESSAGE_TEXT]))
            return
        elif message[ACTION] == EXIT:
            clients.remove(client)
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
