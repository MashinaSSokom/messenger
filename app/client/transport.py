import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
import logging
import json
import threading

from PyQt5.QtCore import pyqtSignal, QObject

from client.client_database import ClientStorage
from common.errors import ServerError
from common.utils import send_message, get_message
from metaclasses import ClientVerifier
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, EXIT, \
    SENDER, \
    DESTINATION, GET_USERS, GET_ACTIVE_USERS, GET_HISTORY, TARGET, ADD_CONTACT, DEL_CONTACT, GET_MESSAGE_HISTORY, \
    GET_CONTACTS, CONNECTION_TRIES
from common.logger import log

logger = logging.getLogger('client_logger')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    # Signals
    new_message = pyqtSignal(str)
    lost_connection = pyqtSignal()

    def __init__(self, address: str, port: int, client_name: str, database: ClientStorage):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self._port = port
        self._address = address
        self._client_name = client_name
        self._database = database
        self._transport = None
        self._connect()

        try:
            self.user_list_update()
            self.contact_list_update()
        except OSError as err:
            if err.errno:
                logger.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            logger.error('Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            logger.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
            # Флаг продолжения работы транспорта.
        self._running = True

    def _connect(self):
        self._transport = socket(AF_INET, SOCK_STREAM)
        # self._transport.settimeout(5)
        connected = False

        for i in range(CONNECTION_TRIES):
            logger.debug(f'Клиент {self._client_name} попытка подключения №{i + 1}')
            try:
                self._transport.connect((self._address, self._port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break

        if not connected:
            logger.error(f'Клиенту {self._client_name} не удалось подключится к серверу!')
            raise ServerError(f'Не удалось установить соединение с сервером')

        logger.debug(f'Клиент {self._client_name} установил соединение с сервером!')

        try:
            with socket_lock:
                send_message(self._transport, self._create_presence())
                # response = get_message(client_socket)
                result = self._process_response(get_message(self._transport))
                # logger.info(f'Клиент {self._client_name} получил от сервера сообщение {response}')
        # TODO: доработать ошибки
        except (OSError, json.JSONDecodeError):
            logger.critical(f'Клиент {self._client_name} потерял соединение с сервером')
            raise ServerError(f'Потеряно соединение с сервером')
        logger.info(
            f'Клиент {self._client_name}({self._address}: {self._port}) подключился к серверу с овтетом: {result}')

    @log
    def user_list_update(self):
        logger.debug(f'Получение списка пользователей')
        request = {
            ACTION: GET_USERS,
            TIME: time.time(),
            SENDER: self._client_name,
            USER: {ACCOUNT_NAME: self._client_name}
        }
        with socket_lock:
            send_message(self._transport, request)
            response = get_message(self._transport)

        if response[RESPONSE] == 200:
            self._database.add_users_to_known(response[MESSAGE_TEXT])
        else:
            logger.error(f'Не удалось получить список пользователей: {response}')

    @log
    def contact_list_update(self):
        logger.debug(f'Получение списка контактов')
        request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            SENDER: self._client_name,
            USER: {ACCOUNT_NAME: self._client_name}
        }
        with socket_lock:
            send_message(self._transport, request)
            response = get_message(self._transport)
        if response[RESPONSE] == 200:
            for contact in response[MESSAGE_TEXT]:
                self._database.add_contact(contact)
        else:
            logger.error(f'Не удалось получить список пользователей: {response}')

    @log
    def _create_presence(self):
        presence = {
            ACTION: PRESENCE,
            TIME: time.time(),
            SENDER: self._client_name,
            USER: {ACCOUNT_NAME: self._client_name}
        }
        logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {self._client_name}')
        return presence

    @log
    def _process_response(self, response):
        logger.debug(f'Разбор ответа от сервера: {response}')
        if RESPONSE in response:
            if response[RESPONSE] == 200:
                return f'200: OK'
            elif response[RESPONSE] == 400:
                raise ServerError(f'{response[ERROR]}')
            else:
                logger.debug(f'Принят неизвестный код ответа {response[RESPONSE]}')
        elif ACTION in response and response[ACTION] == MESSAGE and SENDER in response and DESTINATION in response \
                and MESSAGE_TEXT in response and response[DESTINATION] == self._client_name:
            self._database.save_message(sender=response[SENDER], recipient=self._client_name,
                                        message=response[MESSAGE_TEXT])
            self.new_message.emit(response[SENDER])

    @log
    def add_contact(self, new_contact):
        logger.debug(f'Клиент {self._client_name} добавляет в контакты {new_contact}')
        request = {
            ACTION: ADD_CONTACT,
            TARGET: new_contact,
            TIME: time.time(),
            SENDER: self._client_name,
            USER: {ACCOUNT_NAME: self._client_name}
        }
        with socket_lock:
            send_message(self._transport, request)
            self._process_response(get_message(self._transport))

    @log
    def del_contact(self, contact_to_delete):
        logger.debug(f'Клиент {self._client_name} удаляет контакт {contact_to_delete}')
        request = {
            ACTION: DEL_CONTACT,
            TARGET: contact_to_delete,
            TIME: time.time(),
            SENDER: self._client_name,
            USER: {ACCOUNT_NAME: self._client_name}
        }
        with socket_lock:
            send_message(self._transport, request)
            self._process_response(get_message(self._transport))

    @log
    def send_message(self, destination, message_text):
        logger.debug(f'{self._client_name}: попытка отправить сообщение пользователю{destination}')
        request = {
            ACTION: MESSAGE,
            TIME: time.time(),
            USER: {ACCOUNT_NAME: self._client_name},
            SENDER: self._client_name,
            DESTINATION: destination,
            MESSAGE_TEXT: message_text
        }
        with socket_lock:
            send_message(self._transport, request)
            self._process_response(get_message(self._transport))

    def shutdown(self):
        self._running = False
        request = {
            ACTION: EXIT,
            TIME: time.time(),
            SENDER: self._client_name,
            # ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self._transport, request)
            except OSError:
                pass
        logger.debug('Транспорт завершает работу.')
        time.sleep(0.5)

    def run(self):
        logger.debug(f'Процесс получения сообщений с сервера запущен')

        while self._running:
            time.sleep(1)
            with socket_lock:
                try:
                    self._transport.settimeout(0.5)
                    response = get_message(self._transport)
                except OSError as e:
                    if e.errno:
                        logger.critical(f'Потеряно соедниенние с сервером: {e.errno}')
                        self._running = False
                        self.lost_connection.emit()

                except (
                        ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError,
                        TypeError) as e:
                    logger.error(f'Потеряно соединение с сервером: {e}')
                    self._running = False
                    self.lost_connection.emit()
                else:
                    logger.debug(f'Принято сообщение с сервера: {response}')
                    self._process_response(response)
                finally:
                    self._transport.settimeout(5)
