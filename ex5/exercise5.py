import json
import sys
from random import randint, choice

import requests


# Красивая печать JSON
def print_json(name, d):
    if isinstance(d, str) or d is None:
        print(f"* {name}: **нет**")
        return
    # Печать заголовков
    if isinstance(d, requests.structures.CaseInsensitiveDict):
        print(f"* {name}:")
        print(f"```")
        for k in sorted(k.lower() for k in d.keys()):
            print(f"{k}: {d[k]}")
        print(f"```")
        return
    assert isinstance(d, dict) or isinstance(d, list) or isinstance(d, tuple), f"{d} {type(d)}"
    print(f"* {name}:\n```json\n{json.dumps(d, indent=2)}\n```")


# "application/json; v=1.0": {
#     "schema": {
#         "$ref": "#/components/schemas/Activity"
#     }
# },
def extract_content_object(content: dict):
    assert isinstance(content, dict)
    for k, v in content.items():
        ref = v['schema']['$ref']
        assert isinstance(ref, str)
        return ref
    assert False, f"{content}"


def print_response(resp: requests.Response):
    assert isinstance(resp, requests.Response)
    print(f"* Статус-код ответа: **{resp.status_code} {resp.reason}**")
    print_json('Заголовки ответа', resp.headers)
    if resp.text == '':
        print_json('Тело ответа', '**нет**')
        return
    s = resp.json()
    if isinstance(s, list):
        s = s[:3]
    print_json('Тело ответа', s)


def gen_request(content: dict, id: int):
    assert isinstance(content, dict)
    assert isinstance(id, int)
    obj = extract_content_object(content)
    if obj == "#/components/schemas/Activity":
        return {
            "id": id,
            "title": f"Activity {id}",
            "dueDate": "2023-12-11T22:08:18.7373723+00:00",
            "completed": choice((True, False))
        }
    elif obj == "#/components/schemas/Book":
        return {
            "id": id,
            "title": f"Book {id}",
            "description": f"Description of book {id}",
            "pageCount": randint(100, 1000),
            "excerpt": f"Excerpt of book {id}",
            "publishDate": "2023-12-10T22:15:35.6799574+00:00"
        }
    elif obj == "#/components/schemas/Author":
        return {
            "id": id,
            "idBook": 1,
            "firstName": f"First Name {id}",
            "lastName": f"Last Name {id}"
        }
    elif obj == "#/components/schemas/CoverPhoto":
        return {
            "id": id,
            "idBook": 1,
            "url": "https://placeholdit.imgix.net/~text?txtsize=33&txt=Book 1&w=250&h=350"
        }
    elif obj == "#/components/schemas/User":
        return {
            "id": id,
            "userName": f"User {id}",
            "password": str(randint(100000, 999999)),
        }
    assert False, obj


def do(header: str, path: str, m: str, id: int):
    assert isinstance(header, str)
    assert isinstance(path, str)
    assert isinstance(m, str)
    assert isinstance(id, int)
    print(header, file=sys.stderr)
    print(f"## {header}")
    print()
    print(f"* HTTP-метод: **{m}**")
    url = f'{BASE_URL}{path}'
    print(f"* Полный URL запроса: {url}")
    print(f"* Заголовки запроса: ```accept: text/json; v=1.0```")
    req = '**нет**'
    if m in ['POST', 'PUT', 'PATCH']:
        req = gen_request(schema['requestBody']['content'], id)
    print_json("Тело запроса", req)
    # Выполняем запрос
    if m == 'POST':
        res = requests.post(url, json=req)
    elif m == 'PUT':
        res = requests.put(url, json=req)
    elif m == 'PATCH':
        res = requests.patch(url, json=req)
    elif m == 'GET':
        res = requests.get(url)
    elif m == 'DELETE':
        res = requests.delete(url)
    else:
        assert False, m
    # Печатаем ответ
    print_response(res)
    print()


# Скачиваем описание API в формате Swagger-JSON
# https://fakerestapi.azurewebsites.net/swagger/v1/swagger.json
BASE_URL = 'https://fakerestapi.azurewebsites.net'
r = requests.get(f'{BASE_URL}/swagger/v1/swagger.json')
assert r.status_code == 200
# Результаты будем писать в файл
sys.stdout = open('exercise5.md', 'w', encoding='utf-8')
count = 0  # Количество тест-кейсов
# Разбираем описание API в формате Swagger-JSON
# p - endpoint - путь на сайте
# config - конфигурация этого конкретного EndPoint
for p, config in r.json()['paths'].items():
    for method, schema in config.items():
        m = method.upper()  # HTTP-метод: GET, POST, PUT, PATCH, DELETE
        count += 1  # Увеличиваем количество тест-кейсов
        id = randint(1, 10)  # Генерируем случайный id
        # Подставляем id в путь
        if '{id}' in p or '{idBook}' in p:
            path = p.replace('{id}', str(id))
            if '{idBook}' in p:
                id = 3
                path = p.replace('{idBook}', str(id))
            do(f"{count}. {path} {m}", path, m, id)
            count += 1
            idx = randint(2147483649, 9999999999)
            path = p.replace('{id}', str(idx)).replace('{idBook}', str(idx))
            do(f"{count}. {path} {m} - несуществующий id", path, m, idx)
        else:
            do(f"{count}. {p} {m}", p, m, id)
