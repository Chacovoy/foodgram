FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

# Копирование скрипта инициализации
COPY init_db.sh /app/init_db.sh
RUN chmod +x /app/init_db.sh

# Запуск скрипта инициализации и сервера
CMD ["sh", "-c", "/app/init_db.sh && gunicorn foodgram.wsgi:application --bind 0:8000"]
