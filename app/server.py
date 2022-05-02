""" SERVER LOGIC SCRIPT """
import sys
import threading
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import select
import logging
import json
import time

from common.logger import log
from common.variables import USER, ACTION, ACCOUNT_NAME, RESPONSE, ERROR, TIME, PRESENCE, MESSAGE, MESSAGE_TEXT, \
    DESTINATION, SENDER, EXIT, RESPONSE_200, RESPONSE_400, GET_HISTORY, GET_USERS, GET_ACTIVE_USERS, TARGET, \
    DEFAULT_PORT, MAX_CONNECTIONS, SERVER_TIMEOUT, DESTINATION, SERVER_DATABASE
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from common.utils import argv_parser, get_message, send_message, create_message_to_send
from common.errors import IncorrectDataRecivedError
from logs import config_server_log
from metaclasses import ServerVerifier
from descriptors import Port
from server_database import Storage

from server_gui import MainWindow,  MessagesStats, ConfigWindow, create_messages_stats_model, \
    create_active_clients_model


# Logger initialization
logger = logging.getLogger('server_logger')


new_connection_lock = threading.Lock()
new_connection = False


class Server(threading.Thread, metaclass=ServerVerifier):
    _port = Port()

    def __init__(self, address, port, database: Storage):
        super().__init__()
        self._port = port
        self._address = address
        self._clients = []
        self._messages = []
        self._client_names = {}
        self._database = database

    def _connect(self):
        serv_sock = socket(AF_INET, SOCK_STREAM)
        serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Reuse socket if it's busy
        serv_sock.bind((self._address, self._port))
        serv_sock.listen(MAX_CONNECTIONS)
        serv_sock.settimeout(SERVER_TIMEOUT)
        return serv_sock

    @log
    def create_confirm_exit_message(self, client_name):
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            SENDER: client_name,
        }
        logger.debug(f'Пользователь {client_name} вышел из системы!')
        return message

    @log
    def _process_client_message(self, message: dict, client: socket, messages: list, clients: list, client_names: dict,
                               database: Storage):
        """"""
        global new_connection
        logger.debug(f'Обработка сообщения от клиента : {message}')

        if message[SENDER] and message[ACTION] and message[TIME] and message[SENDER]:
            if message[ACTION] == PRESENCE:
                if message[SENDER] not in client_names.keys():
                    client_names[message[SENDER]] = client
                    client_ip_address, client_port = client.getpeername()
                    database.login_user(message[SENDER], client_ip_address, client_port)
                    send_message(client, RESPONSE_200)
                    with new_connection_lock:
                        new_connection = True
                else:
                    response = RESPONSE_400
                    response[ERROR] = 'Имя пользователя уже занято!'
                    send_message(client, response)
                    clients.remove(client)
                    client.close()
                return
            elif message[ACTION] == MESSAGE and MESSAGE_TEXT in message and DESTINATION in message:
                messages.append(message)
                return
            elif message[ACTION] == GET_USERS:
                users = database.get_all_users()
                response = {
                    ACTION: GET_USERS,
                    MESSAGE_TEXT: ''
                }
                for user in users:
                    response[MESSAGE_TEXT] += f'Пользователь: {user.username} (последний логин - {user.last_login})\n'
                send_message(client, response)
                return
            elif message[ACTION] == GET_ACTIVE_USERS:
                users = database.get_all_active_users()
                response = {
                    ACTION: GET_USERS,
                    MESSAGE_TEXT: ''
                }
                for user in users:
                    response[
                        MESSAGE_TEXT] += f'Пользователь: имя - {user.username}, ip - {user.ip_address}:{user.port} (время логина - {user.login_time})\n'
                send_message(client, response)
                return
            elif message[ACTION] == GET_HISTORY:
                # if MESSAGE[TARGET]:
                response = {
                    ACTION: GET_HISTORY,
                    MESSAGE_TEXT: ''
                }
                history = database.get_login_history(message[TARGET])
                for row in history:
                    response[
                        MESSAGE_TEXT] += f'Пользователь -{row[0]}, ip - {row[1]}:{row[2]}, последний логин - {row[3]}\n'
                send_message(client, response)
                return
            elif message[ACTION] == EXIT:
                database.logout_user(message[SENDER])
                clients.remove(client)
                del client_names[message[SENDER]]
                send_message(client, self.create_confirm_exit_message(message[SENDER]))
                client.close()
                with new_connection_lock:
                    new_connection = True
                return
        send_message(client, RESPONSE_400)
        return

    @log
    def _process_sending_message(self, message: dict, clients: list[socket], client_names: dict):
        """"""

        if message[DESTINATION] in client_names and client_names[message[DESTINATION]] in clients:
            send_message(client_names[message[DESTINATION]], message)
            logger.debug(f'Пользователь {message[SENDER]} отправил сообщение пользователю {message[DESTINATION]}')
        elif message[DESTINATION] in client_names and client_names[message[DESTINATION]] not in clients:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')
            response = RESPONSE_400
            response[ERROR] = f'Пользователль {message[DESTINATION]}  не зарегистрирован на сервере!'
            send_message(client_names[message[SENDER]], response)

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
                        self._process_client_message(get_message(client), client, self._messages, self._clients,
                                               self._client_names, self._database)
                    except IncorrectDataRecivedError:
                        logger.error(f'От клиента {client.getpeername()} приняты некорректные данные. '
                                     f'Соединение закрывается.')
                        self._clients.remove(client)
                        for key, value in dict(self._client_names).items():
                            if value == client:
                                self._database.logout_user(key)
                                del self._client_names[key]
                    except json.JSONDecodeError:
                        logger.error(f'Не удалось декодировать JSON строку, полученную от '
                                     f'клиента {client.getpeername()}. Соединение закрывается.')
                        self._clients.remove(client)
                        for key, value in dict(self._client_names).items():
                            if value == client:
                                self._database.logout_user(key)
                                del self._client_names[key]
                    except Exception as e:
                        logger.error(f'Не удалось обработать сообщение: {client.getpeername()} отключился от '
                                     f'сервера! Ошибка: {e}')
                        for key, value in dict(self._client_names).items():
                            if value == client:
                                self._database.logout_user(key)
                                del self._client_names[key]
                        self._clients.remove(client)

            # Send client data
            if self._messages and send_data_lst:
                for message in self._messages:
                    try:
                        self._process_sending_message(message, send_data_lst, self._client_names)
                    except ConnectionError:
                        logger.error(f'Связь с клиентом {message[DESTINATION]} потеряна')
                        self._clients.remove(self._client_names[message[DESTINATION]])
                        del self._client_names[message[DESTINATION]]
                self._messages.clear()


def main():
    try:
        # Parse launch params
        arguments = argv_parser()
        address = arguments['address']
        port = arguments['port']
        db = Storage()

        server = Server(address, port, db)
        server.daemon = True
        server.start()

        server_app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.statusBar().showMessage('Сервер запущен!')
        main_window.active_clients_table.setModel(create_active_clients_model(db))
        main_window.active_clients_table.resizeColumnsToContents()
        main_window.active_clients_table.resizeRowsToContents()

        def show_messages_stats() -> None:
            global messages_stats
            messages_stats = MessagesStats()
            messages_stats.messages_stats_table.setModel(create_messages_stats_model(db))
            messages_stats.messages_stats_table.resizeColumnsToContents()
            messages_stats.messages_stats_table.resizeRowsToContents()
            messages_stats.show()

        def show_config() -> None:
            global config_window
            config_window = ConfigWindow()
            config_window.db_path.insert(SERVER_DATABASE)
            config_window.db_file.insert('In progress...') #TODO: разделить путь от имени файла в найстроках, либо убрать имя файла из окна конфига
            config_window.ip.insert(address)
            config_window.port.insert(str(port))
            config_window.save_btn.clicked.connect(save_config)
            config_window.show()

        def save_config() -> None: #TODO: доработать настройку конфига через интерфейс + перезапуск после сохранения
            global config_window
            message = QMessageBox()
            message.information(config_window, 'ОК', 'Найстройки успешно сохранены')

        def update_active_users_table() -> None:
            global new_connection
            if new_connection:
                main_window.active_clients_table.setModel(create_active_clients_model(db))
                main_window.active_clients_table.resizeColumnsToContents()
                main_window.active_clients_table.resizeRowsToContents()
                with new_connection_lock:
                    new_connection = False

        timer = QTimer()
        timer.timeout.connect(update_active_users_table)
        timer.start(1000)
        main_window.refresh_button.triggered.connect(update_active_users_table)
        main_window.messages_stats_button.triggered.connect(show_messages_stats)
        main_window.config_button.triggered.connect(show_config)
        server_app.exec_()
    except Exception as e:
        print(e)




if __name__ == '__main__':
    main()
