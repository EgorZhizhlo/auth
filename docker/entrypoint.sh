#!/usr/bin/env bash
set -e

echo "Ожидаю доступности Postgres ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" >/dev/null 2>&1; do
  sleep 2
done
echo "Postgres доступен."

# Создаём db_auth, если ещё не существует
DB_CHECK_CMD="SELECT 1 FROM pg_database WHERE datname='${DB_NAME}';"
DB_CREATE_CMD="CREATE DATABASE \"${DB_NAME}\";"

if psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -tAc "${DB_CHECK_CMD}" | grep -q 1; then
  echo "База ${DB_NAME} уже существует."
else
  echo "Создаю базу ${DB_NAME}..."
  psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c "${DB_CREATE_CMD}"
fi

exec "$@"
