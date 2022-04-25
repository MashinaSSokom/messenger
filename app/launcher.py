"""Лаунчер"""

import subprocess
import sys
import time

PROCESS = []


while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESS.append(subprocess.Popen([f'{sys.executable}', 'server.py'],
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))

        for i in range(2):
            PROCESS.append(subprocess.Popen([f'{sys.executable}', f'client.py'],
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
