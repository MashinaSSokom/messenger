""" CLIENT LOGIC SCRIPT """

import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
import logging
import json
import threading

from logs import config_client_log
from common.client_utils import create_presence, process_response, \
    receive_message_from_server, user_interface

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
    if namespace.n:
        client_name = namespace.n
    else:
        client_name = input('Введите имя пользователя: ')



    logger.info(
        f'Запущен клиент с парамертами: адрес сервера - {namespace.a}, '
        f'порт - {namespace.p}, имя пользователя: {client_name}')

    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((namespace.a, namespace.p))

        send_message(client_socket, create_presence(client_name))

        response = get_message(client_socket)
        logger.info(f'Клиент {client_name} получил от сервера сообщение {response}')
        result = process_response(response)

        logger.info(f'Клиент {client_name}({namespace.a}: {namespace.p}) подключился к серверу с овтетом: {result}')
        print(f'Установлено соединение с сервером. Ответ сервера - {result}')
        print(f'Добро пожаловать, {client_name}! Консольный мессенджер готов к работе ^_^')

    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        print('Произошла ошибка, перезапустите приложение!')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        logger.error(f'В ответе сервера отсутствует необходимое поле '
                     f'{missing_error.missing_field}')
        print('Произошла ошибка, перезапустите приложение!')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(f'Не удалось подключиться к серверу {namespace.a}:{namespace.p}, '
                        f'конечный компьютер отверг запрос на подключение.')
        print('Не удалось подключиться к серверу!')
        sys.exit(1)

    else:

        server_receiver = threading.Thread(target=receive_message_from_server, args=(client_socket, client_name))
        server_receiver.daemon = True
        server_receiver.start()

        client_interface = threading.Thread(target=user_interface, args=(client_socket, client_name))
        client_interface.daemon = True
        client_interface.start()

        logger.debug(f'Клиент {client_name}({namespace.a}: {namespace.p}) завершил запуск процессов')

        # watchdog cycle
        while True:
            time.sleep(1)
            if client_interface.is_alive() and server_receiver.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
