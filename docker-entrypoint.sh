#!/bin/sh
set -eu

APP_PORT="${PORT:-8001}"
DB_PATH="${DATABASE_URL#sqlite:///}"

if [ "${DATABASE_URL#sqlite://}" != "$DATABASE_URL" ] && [ "$DB_PATH" != ":memory:" ]; then
    mkdir -p "$(dirname "$DB_PATH")"
    touch "$DB_PATH"
fi

alembic upgrade head

exec uvicorn main:app --host 0.0.0.0 --port "$APP_PORT"
