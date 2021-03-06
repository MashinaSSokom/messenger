"""Global constants"""

DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 4096
SERVER_TIMEOUT = 0.5
CONNECTION_TRIES = 5
ENCODING = 'utf-8'

# JIM protocol

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

# Database config
SERVER_DATABASE = 'sqlite:///server_base.db3'

# Others
PRESENCE = 'presence'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
RESPONSE = 'response'
ERROR = 'error'
DESTINATION = 'destination'
SENDER = 'sender'
TARGET = 'target'
EXIT = 'exit'
GET_USERS = 'get_users'
GET_ACTIVE_USERS = 'get_active_users'
GET_HISTORY = 'get_history'
GET_CONTACTS = 'get_contacts'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'
GET_MESSAGE_HISTORY = 'get_message_history'
RESPONSE_DEFAULT_IP_ADDRESS = 'response_default_ip_address'

# Default responses

RESPONSE_200 = {
    RESPONSE: 200
}

RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: 'Bad request'
}
