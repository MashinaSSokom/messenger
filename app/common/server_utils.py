from app.common.variables import USER, ACTION, ACCOUNT_NAME, RESPONSE, ERROR, TIME, PRESENCE


def process_client_message(message):
    if [USER, ACTION, TIME].sort() == list(message.keys()).sort() and message[ACTION] == PRESENCE \
            and message[USER][ACCOUNT_NAME]:
        return {
            RESPONSE: 200
        }
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }