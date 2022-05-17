"""Лаунчер"""

import subprocess
import sys
import time

PROCESS = []


while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер, k - запустить клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESS.append(subprocess.Popen([f'{sys.executable}', 'server.py'],
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'k':
        clients_count = int(input('Введите количество клиентов для запуска: '))
        for i in range(clients_count):
            try:
                PROCESS.append(subprocess.Popen([f'{sys.executable}', f'client.py'],
                                           creationflags=subprocess.CREATE_NO_WINDOW))
            except Exception as e:
                print(e)
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
