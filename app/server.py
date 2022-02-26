from socket import socket, AF_INET, SOCK_STREAM
import time
import logging
import json

from common.server_utils import process_client_message
from common.utils import create_argv_parser, get_message, send_message
from common.variables import DEFAULT_PORT
from errors import IncorrectDataRecivedError
from logs import config_client_log

logger = logging.getLogger('server_logger')

parser = create_argv_parser()
namespace = parser.parse_args()

if not namespace.p:
    namespace.p = DEFAULT_PORT
if not namespace.a:
    namespace.a = ''

SERV_SOCK = socket(AF_INET, SOCK_STREAM)
SERV_SOCK.bind((namespace.a, namespace.p))
SERV_SOCK.listen(5)

logger.info(f'Запущен сервер, порт для подключений: {namespace.p}, '
            f'адрес с которого принимаются подключения: {namespace.a}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.')

try:
    while True:
        CLIENT_SOCK, ADDR = SERV_SOCK.accept()
        print(f'Получен запрос на коннект с {ADDR}')

        logger.info(f'Установлено соедение с ПК {ADDR}')
        try:
            message = get_message(CLIENT_SOCK)
            response = process_client_message(message)
            send_message(CLIENT_SOCK, response)
            CLIENT_SOCK.close()

        except json.JSONDecodeError:
            logger.error(f'Не удалось декодировать JSON строку, полученную от '
                                f'клиента {ADDR}. Соединение закрывается.')
            CLIENT_SOCK.close()
        except IncorrectDataRecivedError:
            logger.error(f'От клиента {ADDR} приняты некорректные данные. '
                                f'Соединение закрывается.')
            CLIENT_SOCK.close()
finally:
    SERV_SOCK.close()
