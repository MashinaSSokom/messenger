"""
#2 Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов
(не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.
"""
print('Задание #1')
print(20 * '=' + '\n')

words = ['class', 'function', 'method']


def convert_to_bytes(items: list):
    words_in_bytes = [eval(f"b'{item}'") for item in items]
    for word in words_in_bytes:
        print(f'Слово: {word}')
        print(f'Тип: {type(word)}')
        print(f'Длина: {len(word)}')
        print(10 * '=')


convert_to_bytes(items=words)
