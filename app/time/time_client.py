from socket import socket, AF_INET, SOCK_STREAM

CLIENT_SOCKET = socket(AF_INET, SOCK_STREAM)
CLIENT_SOCKET.connect(('localhost', 8888))
TIME_BYTES = CLIENT_SOCKET.recv(1024)
print(f'Текущее время на сервере: {TIME_BYTES.decode("utf-8")}')
CLIENT_SOCKET.close()
