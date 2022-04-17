""" SERVER LOGIC SCRIPT """

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import select
import logging
import json
from typing import Dict

from common.server_utils import process_client_message, process_sending_message
from common.utils import argv_parser, get_message, send_message, create_message_to_send
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, SERVER_TIMEOUT, DESTINATION
from app.common.errors import IncorrectDataRecivedError
from logs import config_server_log
from metaclasses import ServerVerifier
from descriptors import Port

# Logger initialization
logger = logging.getLogger('server_logger')


class Server(metaclass=ServerVerifier):
    _port = Port()

    def __init__(self, address, port):
        self._port = port
        self._address = address
        self._clients = []
        self._messages = []
        self._client_names = {}

    def _connect(self):
        serv_sock = socket(AF_INET, SOCK_STREAM)
        serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Reuse socket if it's busy
        serv_sock.bind((self._address, self._port))
        serv_sock.listen(MAX_CONNECTIONS)
        serv_sock.settimeout(SERVER_TIMEOUT)
        return serv_sock

    def run(self):

        serv_sock = self._connect()
        logger.info(f'Запущен сервер, порт для подключений: {self._port}, '
                    f'адрес с которого принимаются подключения: {self._address}. '
                    f'Если адрес не указан, принимаются соединения с любых адресов.')

        print(f'Сервер запущен!\n'
              f'Данные для подключения: {self._address if  self._address else "127.0.0.1" }:{self._port}')


        while True:
            # Connect clients
            try:
                client_sock, addr = serv_sock.accept()
                print(f'Получен запрос на коннект с {addr}')
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {addr}')
                self._clients.append(client_sock)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            # Check waiting for receive or sending clients
            try:
                if self._clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self._clients, self._clients, [], 0)
            except OSError:
                pass

            # Receive client data
            if recv_data_lst:
                for client in recv_data_lst:
                    try:
                        process_client_message(get_message(client), client, self._messages, self._clients, self._client_names)
                    except IncorrectDataRecivedError:
                        logger.error(f'От клиента {client.getpeername()} приняты некорректные данные. '
                                     f'Соединение закрывается.')
                        self._clients.remove(client)
                    except json.JSONDecodeError:
                        logger.error(f'Не удалось декодировать JSON строку, полученную от '
                                     f'клиента {client.getpeername()}. Соединение закрывается.')
                        self._clients.remove(client)
                    except Exception as e:
                        logger.error(f'Не удалось обработать сообщение: {client.getpeername()} отключился от '
                                     f'сервера! Ошибка: {e}')
                        self._clients.remove(client)

            # Send client data
            if self._messages and send_data_lst:
                for message in self._messages:
                    try:
                        process_sending_message(message, send_data_lst, self._client_names)
                    except ConnectionError:
                        logger.error(f'Связь с клиентом {message[DESTINATION]} потеряна')
                        self._clients.remove(self._client_names[message[DESTINATION]])
                        del self._client_names[message[DESTINATION]]
                self._messages.clear()


def main():
    # Parse launch params
    arguments = argv_parser()
    address = arguments['address']
    port = arguments['port']
    server = Server(address, port)
    server.run()


if __name__ == '__main__':
    main()
