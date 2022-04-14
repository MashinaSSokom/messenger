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

# Logger initialization
logger = logging.getLogger('server_logger')


def main():
    # Parse launch params
    arguments = argv_parser()

    address = arguments['address']
    port = arguments['port']

    # launch server socket
    with socket(AF_INET, SOCK_STREAM) as serv_sock:
        serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Reuse socket if it's busy
        serv_sock.bind((address, port))
        serv_sock.listen(MAX_CONNECTIONS)
        serv_sock.settimeout(SERVER_TIMEOUT)

        logger.info(f'Запущен сервер, порт для подключений: {port}, '
                    f'адрес с которого принимаются подключения: {address}. '
                    f'Если адрес не указан, принимаются соединения с любых адресов.')

        print(f'Сервер запущен!\n'
              f'Данные для подключения: {address if  address else "127.0.0.1" }:{port}')

        clients = []
        messages = []
        client_names = {}

        while True:
            # Connect clients
            try:
                client_sock, addr = serv_sock.accept()
                print(f'Получен запрос на коннект с {addr}')
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {addr}')
                clients.append(client_sock)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            # Check waiting for receive or sending clients
            try:
                if clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                pass

            # Receive client data
            if recv_data_lst:
                for client in recv_data_lst:
                    try:
                        process_client_message(get_message(client), client, messages, clients, client_names)
                    except IncorrectDataRecivedError:
                        logger.error(f'От клиента {client.getpeername()} приняты некорректные данные. '
                                     f'Соединение закрывается.')
                        clients.remove(client)
                    except json.JSONDecodeError:
                        logger.error(f'Не удалось декодировать JSON строку, полученную от '
                                     f'клиента {client.getpeername()}. Соединение закрывается.')
                        clients.remove(client)
                    except Exception as e:
                        logger.error(f'Не удалось обработать сообщение: {client.getpeername()} отключился от '
                                     f'сервера! Ошибка: {e}')
                        clients.remove(client)

            # Send client data
            if messages and send_data_lst:
                for message in messages:
                    try:
                        process_sending_message(message, send_data_lst, client_names)
                    except ConnectionError:
                        logger.error(f'Связь с клиентом {message[DESTINATION]} потеряна')
                        clients.remove(client_names[message[DESTINATION]])
                        del client_names[message[DESTINATION]]
                messages.clear()

if __name__ == '__main__':
    main()
