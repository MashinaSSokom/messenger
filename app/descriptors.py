import logging
logger = logging.getLogger('server_logger')


class Port:
    def __set__(self, instance, value):

        if not 1023 < value < 65536:
            logger.error(
                f'Некорректное значение порта {value} при попытке запуска сервера'
            )
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
