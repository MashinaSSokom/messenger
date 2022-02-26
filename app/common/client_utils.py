import time

from .variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR


def create_presence(account_name='Guest'):
    return {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {ACCOUNT_NAME: account_name}
    }


def process_response(response):
    if RESPONSE in response:
        if response[RESPONSE] == 200:
            return f'200: OK'
        return f'400: {response[ERROR]}'
    raise ValueError
