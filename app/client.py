from socket import socket, AF_INET, SOCK_STREAM
import time

from common.client_utils import create_presence, process_response
from common.utils import create_argv_parser, get_message, send_message
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS

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
