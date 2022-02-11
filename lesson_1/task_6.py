"""
#5 Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
Далее забыть о том, что мы сами только что создали этот файл
и исходить из того, что перед нами файл в неизвестной кодировке.
Задача: открыть этот файл БЕЗ ОШИБОК вне зависимости от того, в какой кодировке он был создан.
"""
import locale

def_coding = locale.getpreferredencoding()

lines = ['сетевое программирование', 'сокет', 'декоратор']

with open('test_file.txt', 'w') as f:
    f.writelines([f'{line}\n' for line in lines])

with open('test_file.txt', 'r', encoding=def_coding) as f:
    print(f.readlines())
