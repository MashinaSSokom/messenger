'''
#2 Есть файл orders в формате JSON с информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными.
Для этого:
- Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item),
количество (quantity), цена (price), покупатель (buyer), дата (date).
Функция должна предусматривать запись данных в виде словаря в файл orders.json.
При записи данных указать величину отступа в 4 пробельных символа;

- Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
'''
import json


def write_order_to_json(item: str, quantity: int, price: float, buyer: str, date: str):
    new_order = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date
    }
    with open('orders.json', 'r', encoding='utf-8') as f_r:
        data = json.load(f_r)
        orders = data['orders']
    with open('orders.json', 'w', encoding='utf-8') as f_w:
        orders.append(new_order)
        json.dump(data, f_w, indent=4, ensure_ascii=False)


write_order_to_json(item='item1', quantity=1, price=999.99, buyer='buyer1', date='01.01.2000')
write_order_to_json(item='item2', quantity=1, price=999.99, buyer='buyer2', date='01.01.2000')
write_order_to_json(item='item3', quantity=1, price=999.99, buyer='buyer3', date='01.01.2000')
