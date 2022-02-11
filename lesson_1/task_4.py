"""
#4 Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в байтовое
и выполнить обратное преобразование (используя методы encode и decode).
"""

words = ['разработка', 'администрирование', 'protocol', 'standard']


def str_to_bytes_to_str(items: list[str]):
    bytes_items = []
    for item in items:
        bytes_items.append(item.encode('utf-8'))

    print(f'Список в байтовом виде:\n{bytes_items}')

    str_items = []
    for item in bytes_items:
        str_items.append(item.decode('utf-8'))

    print(f'Список в строковом виде:\n{str_items}')


str_to_bytes_to_str(words)
