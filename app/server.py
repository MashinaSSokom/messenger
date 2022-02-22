from socket import socket, AF_INET, SOCK_STREAM
import time

from app.common.server_utils import process_client_message
from app.common.utils import create_argv_parser, get_message, send_message
from app.common.variables import DEFAULT_PORT

parser = create_argv_parser()
namespace = parser.parse_args()

if not namespace.p:
    namespace.p = DEFAULT_PORT
if not namespace.a:
    namespace.a = ''

SERV_SOCK = socket(AF_INET, SOCK_STREAM)
SERV_SOCK.bind((namespace.a, namespace.p))
SERV_SOCK.listen(5)

try:
    while True:
        CLIENT_SOCK, ADDR = SERV_SOCK.accept()
        print(f'Получен запрос на коннект с {ADDR}')
        message = get_message(CLIENT_SOCK)
        response = process_client_message(message)
        send_message(CLIENT_SOCK, response)
        CLIENT_SOCK.close()
finally:
    SERV_SOCK.close()
