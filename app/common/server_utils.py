from .variables import USER, ACTION, ACCOUNT_NAME, RESPONSE, ERROR, TIME, PRESENCE


def process_client_message(message):
    sorted_message_keys = sorted(list(message.keys()))
    sorted_keys = sorted([USER, ACTION, TIME])

    if sorted_keys == sorted_message_keys and message[ACTION] == PRESENCE\
            and message[USER][ACCOUNT_NAME]:
        return {
            RESPONSE: 200
        }
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }