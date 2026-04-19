# auth_py

Python-микросервис для привязки Telegram и Steam аккаунтов.

## Подготовка

```bash
cd auth_py
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Миграции базы данных

Перед запуском сервиса сначала применяйте миграции Alembic.

```bash
cd auth_py
alembic upgrade head
```

Если нужно откатить последнюю миграцию:

```bash
cd auth_py
alembic downgrade -1
```

## Запуск сервиса

После применения миграций:

```bash
cd auth_py
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Запуск в Docker

Сервис поднимается в контейнере с автоматическим применением миграций при старте.
База SQLite хранится в папке `./data` на хосте.

### Требования

- установлен Docker
- установлен Docker Compose

### Сборка и запуск

```bash
docker compose up --build -d
```

Сервис будет доступен на порту `8082`.

### Проверка

```bash
curl http://localhost:8082/link/123
```

Ожидаемый ответ для пустой базы:

```json
{"status":"success","steamId":null}
```

### Просмотр логов

```bash
docker compose logs -f
```

### Остановка

```bash
docker compose down
```

## Полезные команды Alembic

Создать новую миграцию вручную:

```bash
cd auth_py
alembic revision -m "описание изменений"
```

Создать миграцию по изменениям моделей:

```bash
cd auth_py
alembic revision --autogenerate -m "описание изменений"
```

Проверить текущую версию миграций:

```bash
cd auth_py
alembic current
```
