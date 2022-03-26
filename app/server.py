from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import select
import logging
import json

from common.server_utils import process_client_message
from common.utils import create_argv_parser, get_message, send_message, create_message_to_send
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, SERVER_TIMEOUT
from app.common.errors import IncorrectDataRecivedError


def main():
    logger = logging.getLogger('server_logger')

    parser = create_argv_parser()
    namespace = parser.parse_args()

    if not namespace.p:
        namespace.p = DEFAULT_PORT
    if not namespace.a:
        namespace.a = ''

    with socket(AF_INET, SOCK_STREAM) as serv_sock:
        serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serv_sock.bind((namespace.a, namespace.p))
        serv_sock.listen(MAX_CONNECTIONS)
        serv_sock.settimeout(SERVER_TIMEOUT)

        print(logger)
        logger.info(f'Запущен сервер, порт для подключений: {namespace.p}, '
                    f'адрес с которого принимаются подключения: {namespace.a}. '
                    f'Если адрес не указан, принимаются соединения с любых адресов.')

        clients = []
        messages = []

        while True:
            # Подключение клиентов
            try:
                client_sock, addr = serv_sock.accept()
                print(f'Получен запрос на коннект с {addr}')
            except OSError:
                pass
            else:
                logger.debug(f'Установлено соедение с ПК {addr}')
                clients.append(client_sock)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            try:
                if clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client in recv_data_lst:
                    print(client)
                    try:
                        process_client_message(get_message(client), client, messages)

                    # except IncorrectDataRecivedError:
                    #     logger.error(f'От клиента {client.getpeername()} приняты некорректные данные. '
                    #                  f'Соединение закрывается.')
                    #     clients.remove(client)
                    # except json.JSONDecodeError:
                    #     logger.error(f'Не удалось декодировать JSON строку, полученную от '
                    #                  f'клиента {client.getpeername()}. Соединение закрывается.')
                    #     clients.remove(client)

                    except Exception:
                        logger.error(f'Не удалось обработать сообщение: {client.getpeername()} отключился от '
                                     f'сервера!')
                        clients.remove(client)

            if messages and send_data_lst:
                response = create_message_to_send(account_name=messages[0][0], message_text=messages[0][1])
                del messages[0]
                for waiting_client in send_data_lst:
                    try:
                        send_message(waiting_client, response)
                    except:
                        logger.error(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                        waiting_client.close()
                        clients.remove(waiting_client)


if __name__ == '__main__':
    main()
