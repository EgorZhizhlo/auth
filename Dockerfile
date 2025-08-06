FROM python:3.12-slim

# 1. Системные утилиты (psql нужен только для entrypoint’а)
RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-client \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /auth_service

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код приложения
COPY . .

# скрипт, который ждёт Postgres и создаёт БД, если её нет
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
