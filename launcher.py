"""Лаунчер"""

import subprocess
import time

PROCESS = []



while True:

    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESS.append(subprocess.Popen('python app/server.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(1):
            PROCESS.append(subprocess.Popen('python app/client.py -m send',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(3):
            PROCESS.append(subprocess.Popen('python app/client.py -m listen',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
