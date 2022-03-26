import logging

from .logger import log
from .variables import USER, ACTION, ACCOUNT_NAME, RESPONSE, ERROR, TIME, PRESENCE, MESSAGE, MESSAGE_TEXT
from .utils import send_message

# from ..logs import config_client_log

logger = logging.getLogger('server_logger')


@log
def process_client_message(message, client, messages=[]):
    logger.debug(f'Обработка сообщения от клиента : {message}')

    sorted_message_keys = sorted(list(message.keys()))
    sorted_keys = sorted([USER, ACTION, TIME])

    if sorted_keys == sorted_message_keys and message[USER][ACCOUNT_NAME]:
        if message[ACTION] == PRESENCE:

            send_message(client, {
                 RESPONSE: 200
             })
            return

        elif message[ACTION] == MESSAGE and MESSAGE_TEXT in message:
            messages.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
            return

    send_message(client, {
        RESPONSE: 400,
        ERROR: 'Bad request'
    })
    return
