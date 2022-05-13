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


class ClientTransport(metaclass=ClientVerifier, threading.Thread, QObject):
    # Signals
    new_messasge = pyqtSignal(str)
    lost_connection = pyqtSignal()

    def __init__(self, address: str, port: int, client_name: str, database: ClientStorage):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self._port = port
        self._address = address
        self._client_name = client_name
        self._database = database
        self._transport = None

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
                if ACTION in response and response[ACTION] == MESSAGE and SENDER in response and DESTINATION in response \
                        and MESSAGE_TEXT in response and response[DESTINATION] == self._client_name:
                    self._database.save_message(sender=response[SENDER], recipient=response[self._client_name],
                                                message=response[MESSAGE_TEXT])
                    self.new_messasge.emit(response[SENDER])
                return f'200: OK'
            elif response[RESPONSE] == 400:
                raise ServerError(f'{response[ERROR]}')
            else:
                logger.debug(f'Принят неизвестный код ответа {response[RESPONSE]}')
