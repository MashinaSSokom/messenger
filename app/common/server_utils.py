import logging
import threading
from socket import socket
import time

from .logger import log
from .variables import USER, ACTION, ACCOUNT_NAME, RESPONSE, ERROR, TIME, PRESENCE, MESSAGE, MESSAGE_TEXT, \
    DESTINATION, SENDER, EXIT, RESPONSE_200, RESPONSE_400, GET_HISTORY, GET_USERS, GET_ACTIVE_USERS, TARGET, \
    new_connection
from .utils import send_message
from server_database import Storage
# from ..logs import config_client_log

logger = logging.getLogger('server_logger')

new_connection_lock = threading.Lock()
print(new_connection)

