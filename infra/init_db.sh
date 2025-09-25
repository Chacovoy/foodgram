#!/bin/bash

# Ожидание готовности базы данных
echo "Ожидание готовности базы данных..."
while ! pg_isready -h db -p 5432 -U foodgram_user; do
  echo "База данных не готова, ждем..."
  sleep 2
done

echo "База данных готова!"

# Применение миграций
echo "Применение миграций..."
python manage.py migrate

# Создание суперпользователя
echo "Создание суперпользователя..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Суперпользователь создан: admin/admin123')
else:
    print('Суперпользователь уже существует')
"

# Загрузка данных
echo "Загрузка ингредиентов..."
python manage.py load_ingredients_data

echo "Загрузка тегов..."
python manage.py load_tags_data

# Сбор статических файлов
echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

echo "Инициализация завершена!"
