"""
#3 Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
Важно: решение должно быть универсальным, т.е. не зависеть от того, какие конкретно слова мы исследуем.
"""

words = ['attribute', 'функция', 'type']


def convert_to_bytes_checker(item: str):
    for letter in item:
        if ord(letter) > 127:
            return f'Слово {item} невозможно записать в байтовом виде! :('
    return f'Слово {item} возможно записать в байтовой виде! :)'


for word in words:
    print(convert_to_bytes_checker(word))
