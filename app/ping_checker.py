"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или
ip-адресом. В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции
ip_address().
"""

from ipaddress import ip_address
from subprocess import Popen, PIPE
from tabulate import tabulate


def host_ping(ip_addresses: list, timeout: int = 500, number_of_requests: int = 1) -> dict:
    res = {'available': [], 'not_available': []}
    for address in ip_addresses:
        try:
            address = ip_address(address)
        except ValueError:
            pass
        p = Popen(f'ping {address} -n {number_of_requests} -w {timeout}', shell=False, stdout=PIPE)
        p.wait()
        if p.returncode == 0:
            res['available'].append(f'{str(address)}')
            print(f'{address} - доступен')
        else:
            res['not_available'].append(f'{str(address)}')
            print(f'{address} - недоступен')
    return res


print(f'\n--- Задание #1 ---')
addresses = ['192.168.0.1', 'gb.ru', '140.82.121.4']
res = host_ping(addresses)
print(res)

"""
Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только 
последний октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение. 
"""


def host_range_ping(start_ip: str, end_ip: str) -> dict:
    try:
        start_last_octet = int(start_ip.split('.')[3])
        end_last_octet = int(end_ip.split('.')[3])
        start_ip = ip_address(start_ip)
        end_ip = ip_address(end_ip)
        if (int(end_ip) - int(start_ip) > 256) or (str(start_ip).split('.')[0:3] != str(end_ip).split('.')[0:3]):
            raise ValueError(f'Превышен диапазон изменения Ip-адреса '
                             f'(начальный и конечный ip могут отличаться только последним октетом)')
    except Exception as e:
        raise ValueError(e)

    ip_addresses = [str(start_ip + i) for i in range(end_last_octet - start_last_octet + 1)]
    return host_ping(ip_addresses)


print(f'\n--- Задание #2 ---')
host_range_ping('140.82.121.0', '140.82.121.5')

"""
Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2. Но в данном случае 
результат должен быть итоговым по всем ip-адресам, представленным в табличном формате (использовать модуль tabulate). 
Таблица должна состоять из двух колонок и выглядеть примерно так: 

Reachable
10.0.0.1
10.0.0.2

Unreachable
10.0.0.3
10.0.0.4
"""


def host_range_ping_tab(start_ip: str, end_ip: str):
    res = host_range_ping(start_ip, end_ip)
    print(tabulate(res, headers='keys', tablefmt='grid'))

print(f'\n--- Задание #3 ---')
host_range_ping_tab('140.82.121.0', '140.82.121.5')
