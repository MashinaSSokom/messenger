'''
#3 Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата.
Для этого:
- Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список,
второму — целое число, третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом,
отсутствующим в кодировке ASCII (например, €);

- Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
При этом обеспечить стилизацию файла с помощью параметра default_flow_style,
а также установить возможность работы с юникодом: allow_unicode = True;

- Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.
'''
import yaml

test_data = {'products': ['mouse', 'headphones', 'smartphone'],
             'total_price': 3,
             'products_price': {'mouse': '50$', 'headphones': '25$', 'smartphone': '500$'}}


def write_to_yaml(data):
    with open('task_3.yaml', 'w', encoding='utf-8') as f_w:
        yaml.dump(data, f_w, default_flow_style=False, allow_unicode=True, sort_keys=False)


def read_from_yaml(filename):
    with open(filename, 'r', encoding='utf-8') as f_r:
        return yaml.load(f_r, Loader=yaml.SafeLoader)


write_to_yaml(data=test_data)
print(test_data == read_from_yaml('task_3.yaml'))
