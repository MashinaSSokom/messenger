'''
#1 Написать скрипт, осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt, info_3.txt
и формирующий новый «отчетный» файл в формате CSV.
Для этого:
- Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие
и считывание данных. В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь
значения параметров «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список.
Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list, os_type_list.
В этой же функции создать главный список для хранения данных отчета — например,
main_data — и поместить в него названия столбцов отчета в виде списка:
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);

- Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

- Проверить работу программы через вызов функции write_to_csv().
'''
import csv
import os
import re
from chardet import detect


def get_data():
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    dir_names_reg = re.compile(r'info.+\.txt')
    file_names = dir_names_reg.findall(" ".join(os.listdir()))[0].split(' ')
    for file in file_names:
        with open(file, 'rb') as f_r:
            file_b = f_r.read()
            data = file_b.decode(encoding=detect(file_b)['encoding'])

        os_prod_re = re.compile(r'Изготовитель системы:\s*\w*')
        os_prod = os_prod_re.findall(data)[0].split()[2]
        os_prod_list.append(os_prod)

        os_name_re = re.compile(r'Название ОС:\s*.*\S')
        os_name = " ".join(os_name_re.findall(data)[0].split()[2:])
        os_name_list.append(os_name)

        os_code_re = re.compile(r'Код продукта:\s*\S*')
        os_code = os_code_re.findall(data)[0].split()[2]
        os_code_list.append(os_code)

        os_type_re = re.compile(r'Тип системы:\s*\S*')
        os_type = os_type_re.findall(data)[0].split()[2]
        os_type_list.append(os_type)

    main_data = []
    all_data = [os_prod_list, os_name_list, os_code_list, os_type_list]
    for idx in range(len(file_names)):
        line = [row[idx] for row in all_data]
        main_data.append(line)
    headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data.insert(0, headers)

    return main_data


def write_to_csv(filename: str, data: dict):
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        try:
            csv_writer = csv.writer(f)
            csv_writer.writerows(data)
            print(f'Файл успешно создан!')
        except Exception as e:
            print(f'Произошла ошибка!\n{e}')


write_to_csv('task_1.csv', get_data())

