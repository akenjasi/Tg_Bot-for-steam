import os
import time
from datetime import datetime

import requests

base = os.getenv("AUTH_SERVICE_URL", "http://localhost:8082")
print("тестируем сервис...\n")

required_fields = {"status", "message", "steamId"}
suffix = str(int(datetime.now().timestamp()))[-6:]
telegram_id = int(f"123{suffix}")
duplicate_telegram_id = telegram_id
other_telegram_id = int(f"456{suffix}")
missing_telegram_id = int(f"999{suffix}")
steam_id = f"76561198000{suffix}"
other_steam_id = f"76561199000{suffix}"

assert len(steam_id) == 17
assert len(other_steam_id) == 17


def print_response(response):
    response_json = response.json()
    print(f"статус: {response.status_code}")
    print(f"ответ: {response_json}\n")
    return response_json

print("1 создаем привязку")
r = requests.post(
    f"{base}/bind",
    json={
        "telegramId": telegram_id,
        "steamLink": f"https://steamcommunity.com/profiles/{steam_id}/",
    },
)
response_json = print_response(r)
print(f"контракт bind: {required_fields.issubset(response_json.keys())}")
time.sleep(1)

print("2 получаем steam id")
r = requests.get(f"{base}/link/{telegram_id}")
print_response(r)
time.sleep(1)

print("3 пробуем тот же telegram")
r = requests.post(
    f"{base}/bind",
    json={
        "telegramId": duplicate_telegram_id,
        "steamLink": f"https://steamcommunity.com/profiles/{other_steam_id}/",
    },
)
response_json = print_response(r)
print(f"контракт bind: {required_fields.issubset(response_json.keys())}")
time.sleep(1)

print("4 пробуем тот же steam")
r = requests.post(
    f"{base}/bind",
    json={
        "telegramId": other_telegram_id,
        "steamLink": f"https://steamcommunity.com/profiles/{steam_id}/",
    },
)
response_json = print_response(r)
print(f"контракт bind: {required_fields.issubset(response_json.keys())}")
time.sleep(1)

print("5 неправильная ссылка")
r = requests.post(
    f"{base}/bind",
    json={
        "telegramId": 789,
        "steamLink": "https://steamcommunity.com/id/vasya/",
    },
)
response_json = print_response(r)
print(f"контракт bind: {required_fields.issubset(response_json.keys())}")
time.sleep(1)

print("6 несуществующий telegram")
r = requests.get(f"{base}/link/{missing_telegram_id}")
print_response(r)
