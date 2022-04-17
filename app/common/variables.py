"""Global constants"""

DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
SERVER_TIMEOUT = 0.5
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
EXIT = 'exit'
RESPONSE_DEFAULT_IP_ADDRESS = 'response_default_ip_address'

# Default responses

RESPONSE_200 = {
    RESPONSE: 200
}

RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: 'Bad request'
}
