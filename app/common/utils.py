import argparse
import json
import time

from .logger import log
from .variables import MAX_PACKAGE_LENGTH, ENCODING, ACTION, TIME, MESSAGE_TEXT, ACCOUNT_NAME, MESSAGE
from .errors import IncorrectDataRecivedError


@log
def create_argv_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', nargs='?')
    parser.add_argument('-p', type=int, nargs='?')
    return parser


@log
def get_message(socket):
    encoded_message = socket.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_message, bytes):
        json_response = encoded_message.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataRecivedError
    raise IncorrectDataRecivedError


@log
def send_message(socket, message):
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    socket.send(encoded_message)


@log
def create_message_to_send(account_name, message_text):
    message = {
        ACTION: MESSAGE,
        ACCOUNT_NAME: account_name,
        TIME: time.time(),
        MESSAGE_TEXT: message_text
    }
    return message
