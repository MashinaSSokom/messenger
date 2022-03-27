import sys
from socket import socket, AF_INET, SOCK_STREAM
import logging
import json

from logs import config_client_log
from common.client_utils import create_presence, process_response, create_message, message_from_server
from common.utils import create_argv_parser, get_message, send_message
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS
from common.errors import ReqFieldMissingError

logger = logging.getLogger('client_logger')


def main():
    parser = create_argv_parser()
    namespace = parser.parse_args()

    if not namespace.p:
        namespace.p = DEFAULT_PORT
    if not namespace.a:
        namespace.a = DEFAULT_IP_ADDRESS

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {namespace.a}, '
        f'порт: {namespace.p}, режим работы: {namespace.m}')

    try:

        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((namespace.a, namespace.p))

        send_message(client_socket, create_presence())

        response = get_message(client_socket)
        result = process_response(response)

        logger.info(f'Установлено соединение с сервером. Ответ сервера: {result}')
        print(f'Установлено соединение с сервером. Ответ сервера - {result}')

    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
    except ReqFieldMissingError as missing_error:
        logger.error(f'В ответе сервера отсутствует необходимое поле '
                     f'{missing_error.missing_field}')
    except ConnectionRefusedError:
        logger.critical(f'Не удалось подключиться к серверу {namespace.a}:{namespace.p}, '
                        f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)

    else:
        if namespace.m == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            if namespace.m == 'send':
                try:
                    send_message(client_socket, create_message(client_socket))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    logger.error(f'Соединение с сервером {namespace.a} было потеряно.')
                    sys.exit(1)

            if namespace.m == 'listen':
                try:
                    message_from_server(get_message(client_socket))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    logger.error(f'Соединение с сервером {namespace.a} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
