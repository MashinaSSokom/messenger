from socket import socket, AF_INET, SOCK_STREAM
import time
from app.common.utils import create_argv_parser, get_message, send_message
from app.common.variables import DEFAULT_PORT, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR

parser = create_argv_parser()
namespace = parser.parse_args()

if not namespace.p:
    namespace.p = DEFAULT_PORT

SERV_SOCK = socket(AF_INET, SOCK_STREAM)
SERV_SOCK.bind(('', namespace.p))
SERV_SOCK.listen(5)


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


process_client_message({ACTION: 'PRESENCE', USER: {ACCOUNT_NAME: 'GUEST'}, TIME: time.time()})

try:
    while True:
        CLIENT_SOCK, ADDR = SERV_SOCK.accept()
        print(f'Получен запрос на соединение от клиента с адресом и портом {ADDR}')
        message = get_message(CLIENT_SOCK)
        response = process_client_message(message)
        send_message(CLIENT_SOCK, response)
        CLIENT_SOCK.close()
finally:
    SERV_SOCK.close()
