import sys

print(sys.path)
from socket import socket, AF_INET, SOCK_STREAM
import time
from common.utils import create_argv_parser, get_message, send_message
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, \
    ERROR

def create_presence(account_name='Guest'):
    return {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {ACCOUNT_NAME: account_name}
    }


def process_response(response):
    if RESPONSE in response:
        if response[RESPONSE] == 200:
            return f'200: OK'
        return f'400: {response[ERROR]}'
    return ValueError


parser = create_argv_parser()
namespace = parser.parse_args()

if not namespace.p:
    namespace.p = DEFAULT_PORT
if not namespace.a:
    namespace.a = DEFAULT_IP_ADDRESS

CLIENT_SOCKET = socket(AF_INET, SOCK_STREAM)
CLIENT_SOCKET.connect((namespace.a, namespace.p))

message = create_presence()
send_message(CLIENT_SOCKET, message)

response = get_message(CLIENT_SOCKET)
result = process_response(response)
print(result)
CLIENT_SOCKET.close()
