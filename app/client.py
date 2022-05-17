""" CLIENT LOGIC SCRIPT """

import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
import logging
import json
import threading

from PyQt5.QtWidgets import QApplication

from client.transport import ClientTransport
from logs import config_client_log
from common.client_utils import create_presence, process_response, \
    receive_message_from_server, user_interface, load_users_from_server

from common.utils import argv_parser, get_message, send_message
from common.errors import ReqFieldMissingError, ServerError
from metaclasses import ClientVerifier
from client.client_database import ClientStorage
from client.client_gui import ClientNameDialog, ClientMainWindow, AddContactDialog, DeleteContactDialog

logger = logging.getLogger('client_logger')


class Client(metaclass=ClientVerifier):

    def __init__(self, address: str, port: int, client_name: str, database: ClientStorage):
        self._port = port
        self._address = address
        self._client_name = client_name
        self._database = database

    def _connect(self):
        try:
            client_socket = socket(AF_INET, SOCK_STREAM)
            client_socket.connect((self._address, self._port))

            send_message(client_socket, create_presence(self._client_name))
            response = get_message(client_socket)
            logger.info(f'Клиент {self._client_name} получил от сервера сообщение {response}')
            result = process_response(response)
            if result == f'200: OK':
                logger.info(
                    f'Клиент {self._client_name}({self._address}: {self._port}) подключился к серверу с овтетом: {result}')
                print(f'Установлено соединение с сервером')
                print(f'Обновляем список пользователей...')
                # TODO: добавить обработку ошибок и вынести все в отдельную функцию подгрузки пользователей
                try:
                    users = load_users_from_server(client_socket, self._client_name, self._database)
                    self._database.add_users_to_known(users)
                    print(f'Добро пожаловать, {self._client_name}! Консольный мессенджер готов к работе ^_^')
                    return client_socket
                except ServerError as e:
                    print('Не удалось загрузить список пользователей, повторите попытку позже...')
                    logger.error(f'Пользователю {self._client_name} не удалось загрузить список пользователей: {e}')
            logger.error(f'Ошибка подключения к серверу {result}')
            print(f'Ошибка подключения к серверу {result}. Повторите попытку позже...')
            sys.exit(1)
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
            logger.critical(f'Не удалось подключиться к серверу {self._address}:{self._port}, '
                            f'конечный компьютер отверг запрос на подключение.')
            print('Не удалось подключиться к серверу!')
            sys.exit(1)

    def run(self):

        logger.info(
            f'Запукск клиента с парамертами: адрес сервера - {self._address}, '
            f'порт - {self._port}, имя пользователя: {self._client_name}')

        client_socket = self._connect()

        server_receiver = threading.Thread(target=receive_message_from_server,
                                           args=(client_socket, self._client_name, self._database))
        server_receiver.daemon = True
        server_receiver.start()

        client_interface = threading.Thread(target=user_interface,
                                            args=(client_socket, self._client_name, self._database))
        client_interface.daemon = True
        client_interface.start()

        logger.debug(f'Клиент {self._client_name}({self._address}: {self._port}) завершил запуск процессов')

        # watchdog cycle
        while True:
            time.sleep(1)
            if client_interface.is_alive() and server_receiver.is_alive():
                continue
            break


def main():
    arguments = argv_parser()
    address = arguments['address']
    port = arguments['port']
    client_name = arguments['client_name']
    client_app = QApplication(sys.argv)

    if not client_name:
        start_dialog = ClientNameDialog()
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    client_database = ClientStorage(client_name)

    try:
        transport = ClientTransport(address, port, client_name, client_database)
    except ServerError as e:
        logger.error(f'Произошла ошибка подключения к серверу: {e}')
        exit(1)

    transport.setDaemon(True)
    transport.start()

    client_main_window = ClientMainWindow(client_database, transport)
    client_main_window.make_connection(transport)
    client_main_window.setWindowTitle(f'Messenger v1.0 - {client_name}')
    # # client = Client(address, port, client_name, client_database)
    client_app.exec_()

    transport.shutdown()
    transport.join()


if __name__ == '__main__':
    main()
