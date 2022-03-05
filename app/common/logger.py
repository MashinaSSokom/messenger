import logging
import sys
import traceback

module_path = sys.argv[0]
module_name = module_path.split('/')[-1]


def get_logger(module):
    if module == 'client.py':
        return logging.getLogger('client_logger')
    elif module == 'server.py':
        return logging.getLogger('server_logger')

    raise ValueError


logger = get_logger(module_name)


def log(func):
    def wrap(*args, **kwargs):
        logger.debug(f'Вызвана функция {func.__name__} из функции {traceback.format_stack()[0].strip().split()[-1]} '
                     f'Аргументы функции {args} и {kwargs}')
        res = func(*args, **kwargs)
        return res
    return wrap
