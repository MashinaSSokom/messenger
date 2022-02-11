"""
#5 Выполнить пинг веб-ресурсов yandex.ru, youtube.com
и преобразовать результаты из байтовового в строковый тип на кириллице.
"""

import platform
import subprocess
from chardet import detect

urls = ['yandex.ru', 'youtube.com']
param = '-n' if platform.system().lower() == 'windows' else '-c'


def ping_urls(urls: list[str], param: str):
    for url in urls:
        args = ['ping', param, '4', url]
        ping = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in ping.stdout:
            resp = detect(line)
            print(resp)
            line = line.decode(resp['encoding']).encode('utf-8')
            print(line.decode('utf-8'))
        print('\n' + 30 * '=' + '\n')


ping_urls(urls, param)
