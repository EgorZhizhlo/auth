#!/usr/bin/env bash
set -e

# ───────────────────────────────────────────────────────────────
#  Берём пароль из переменной окружения,
#  чтобы psql / pg_isready работали без интерактивного ввода
# ───────────────────────────────────────────────────────────────
export PGPASSWORD="${DB_PASSWORD}"

echo "Ожидаю доступности Postgres ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" >/dev/null 2>&1; do
  sleep 2
done
echo "Postgres доступен."

# Проверяем наличие базы db_auth
DB_CHECK_CMD="SELECT 1 FROM pg_database WHERE datname='${DB_NAME}';"
DB_CREATE_CMD="CREATE DATABASE \"${DB_NAME}\";"

if psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -tAc "${DB_CHECK_CMD}" | grep -q 1; then
  echo "База ${DB_NAME} уже существует."
else
  echo "Создаю базу ${DB_NAME}..."
  psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c "${DB_CREATE_CMD}"
fi

# передаём управление uvicorn (CMD из Dockerfile)
exec "$@"
