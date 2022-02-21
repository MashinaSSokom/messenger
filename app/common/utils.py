import argparse
import json

from app.common.variables import MAX_PACKAGE_LENGTH, ENCODING


def create_argv_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', nargs='?')
    parser.add_argument('-p', nargs='?')
    return parser


def get_message(socket):
    encoded_message = socket.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_message, bytes):
        json_response = encoded_message.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        return ValueError
    return ValueError


def send_message(socket, message):
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    socket.send(encoded_message)
