# Сервис привязки Telegram ↔ Steam

Отдельный HTTP-сервис для модуля Арсения. Он нужен, чтобы связать `telegramId` пользователя с его `steam_id64` и дать другим модулям доступ к этой привязке по HTTP.

## Что делает сервис

- принимает `telegramId` и `steamLink`
- сохраняет привязку `telegram_id -> steam_id64`
- позволяет получить текущую привязку
- позволяет удалить привязку

## Быстрый старт

### Требования

- установлен Docker
- установлен Docker Compose
- у пользователя есть доступ к Docker daemon

### Запуск

```bash
docker compose up --build -d
```

### Проверка

```bash
docker compose ps
curl http://localhost:8082/link/123
```

Ожидаемый ответ для пустой базы:

```json
{"status":"success","steamId":null}
```

Сервис доступен с хоста на порту `8082`.

## Контракт API для команды

Базовый адрес при локальном запуске:

```text
http://localhost:8082
```

### `POST /bind`

Назначение: создать привязку Telegram-аккаунта к Steam-аккаунту.

Пример запроса:

```bash
curl -X POST http://localhost:8082/bind \
  -H "Content-Type: application/json" \
  -d '{
    "telegramId": 123,
    "steamLink": "https://steamcommunity.com/profiles/76561198000000000"
  }'
```

Успешный ответ:

```json
{
  "status": "success",
  "message": "Аккаунт привязан",
  "steamId": "76561198000000000"
}
```

Основные ошибки:

- `400` если Steam-ссылка некорректна
- `409` если этот Telegram уже привязан
- `409` если этот Steam уже привязан

### `GET /link/{telegramId}`

Назначение: получить привязанный `steam_id64` по `telegramId`.

Пример запроса:

```bash
curl http://localhost:8082/link/123
```

Успешный ответ, если привязка есть:

```json
{
  "status": "success",
  "steamId": "76561198000000000"
}
```

Успешный ответ, если привязки нет:

```json
{
  "status": "success",
  "steamId": null
}
```

### `DELETE /link/{telegramId}`

Назначение: удалить привязку по `telegramId`.

Пример запроса:

```bash
curl -X DELETE http://localhost:8082/link/123
```

Успешный ответ:

```json
{
  "status": "success",
  "message": "Привязка удалена"
}
```

Основные ошибки:

- `404` если привязка не найдена

## Как использовать мой сервис из других модулей

- локально обращаться к сервису по адресу `http://localhost:8082`
- использовать только HTTP API как контракт между модулями
- не читать SQLite напрямую и не зависеть от внутренней структуры БД
- для проверки наличия привязки использовать `GET /link/{telegramId}`
- для создания привязки использовать `POST /bind`

## Как это устроено

- приложение написано на `FastAPI`
- база данных: `SQLite`
- данные сохраняются в Docker volume `auth_service_data`
- миграции `Alembic` применяются автоматически при старте контейнера
- при обычных `docker compose down` и `docker compose up` данные сохраняются
- данные удаляются только при `docker compose down -v`

Поддерживаемый формат Steam-ссылки в текущей реализации:

```text
https://steamcommunity.com/profiles/<steam_id64>
```

## Если что-то пошло не так

### Ошибка доступа к Docker daemon

Если `docker compose` пишет `permission denied ... docker.sock`, проблема не в проекте, а в доступе текущего пользователя к Docker daemon.

Проверка:

```bash
id
ls -l /var/run/docker.sock
```

Если пользователя нет в группе `docker`:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

После этого повторите запуск:

```bash
docker compose up --build -d
docker compose logs --tail=100
```

### Полный сброс данных

```bash
docker compose down -v
docker compose up --build -d
```

### Просмотр логов

```bash
docker compose logs -f
```

## Локальный запуск без Docker

Этот сценарий нужен только для локальной разработки.

### Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Применение миграций

```bash
alembic upgrade head
```

### Запуск сервиса

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Полезные команды Alembic

Создать новую миграцию вручную:

```bash
alembic revision -m "описание изменений"
```

Создать миграцию по изменениям моделей:

```bash
alembic revision --autogenerate -m "описание изменений"
```

Проверить текущую версию миграций:

```bash
alembic current
```
