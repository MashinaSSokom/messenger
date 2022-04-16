import argparse
import json
import time
import logging
import sys

from .logger import log
from .variables import MAX_PACKAGE_LENGTH, ENCODING, ACTION, TIME, MESSAGE_TEXT, ACCOUNT_NAME, MESSAGE, USER, \
    DEFAULT_PORT, DEFAULT_IP_ADDRESS
from .errors import IncorrectDataRecivedError


@log
def argv_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', nargs='?')
    parser.add_argument('port', type=int, nargs='?')
    parser.add_argument('-n', nargs='?')

    namespace = parser.parse_args(sys.argv[1:])

    address = namespace.addr if namespace.addr else DEFAULT_IP_ADDRESS
    port = namespace.port if namespace.port else DEFAULT_PORT

    if namespace.n:
        client_name = namespace.n
        return {'address': address, 'port': port, 'client_name': client_name}
    return {'address': address, 'port': port, 'client_name': None}


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
        USER: {ACCOUNT_NAME:account_name},
        TIME: time.time(),
        MESSAGE_TEXT: message_text
    }
    return message
