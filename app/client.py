from socket import socket, AF_INET, SOCK_STREAM
import time
import logging
import json

from common.client_utils import create_presence, process_response
from common.utils import create_argv_parser, get_message, send_message
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS
from errors import ReqFieldMissingError, IncorrectDataRecivedError
from logs import config_client_log

logger = logging.getLogger('client_logger')

parser = create_argv_parser()
namespace = parser.parse_args()

if not namespace.p:
    namespace.p = DEFAULT_PORT
if not namespace.a:
    namespace.a = DEFAULT_IP_ADDRESS
try:
    CLIENT_SOCKET = socket(AF_INET, SOCK_STREAM)
    CLIENT_SOCKET.connect((namespace.a, namespace.p))

    message = create_presence()
    send_message(CLIENT_SOCKET, message)

    response = get_message(CLIENT_SOCKET)
    logger.info(f'Принят ответ от сервера {response}')
    result = process_response(response)

    print(result)
    CLIENT_SOCKET.close()

except json.JSONDecodeError:
    logger.error('Не удалось декодировать полученную Json строку.')
except ReqFieldMissingError as missing_error:
    logger.error(f'В ответе сервера отсутствует необходимое поле '
                 f'{missing_error.missing_field}')
except ConnectionRefusedError:
    logger.critical(f'Не удалось подключиться к серверу {namespace.a}:{namespace.p}, '
                    f'конечный компьютер отверг запрос на подключение.')
