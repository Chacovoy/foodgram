# Foodgram - Продуктовый помощник

[![Deploy](https://github.com/chacovoy/foodgram/actions/workflows/deploy.yml/badge.svg)](https://github.com/chacovoy/foodgram/actions/workflows/deploy.yml)

## Описание

Foodgram - это веб-приложение для публикации рецептов, подписки на авторов, добавления рецептов в избранное и список покупок.

🌐 **Демо:** https://foodgrammm.3utilities.com

## Возможности

- 📝 Публикация рецептов с фото и описанием
- 👥 Подписка на авторов
- ⭐ Добавление рецептов в избранное
- 🛒 Формирование списка покупок
- 🏷️ Фильтрация по тегам
- 👤 Управление профилем и аватаром
- 📱 Адаптивный дизайн

## Технологии

**Backend:**
- Python 3.9
- Django 4.2
- Django REST Framework
- PostgreSQL
- Gunicorn

**Frontend:**
- React
- JavaScript

**DevOps:**
- Docker & Docker Compose
- Nginx
- GitHub Actions
- SSL (Let's Encrypt)

## Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/chacovoy/foodgram.git
cd foodgram
```

### 2. Локальная разработка
```bash
cd infra
docker-compose up -d
```

### 3. Деплой на сервер
Настройте GitHub Secrets:
- `HOST` - IP сервера
- `USERNAME` - имя пользователя
- `SSH_KEY` - приватный SSH ключ
- `SECRET_KEY` - Django secret key
- `DB_NAME` - имя базы данных
- `POSTGRES_USER` - пользователь PostgreSQL
- `POSTGRES_PASSWORD` - пароль PostgreSQL
- `DOCKER_USERNAME` - логин Docker Hub
- `DOCKER_PASSWORD` - пароль Docker Hub
- `DOMAIN_NAME` - доменное имя

Пуш в main автоматически запустит деплой.

## API

Документация API доступна по адресу: `/api/docs/`

**Основные эндпоинты:**
- `/api/users/` - управление пользователями
- `/api/recipes/` - рецепты
- `/api/tags/` - теги
- `/api/ingredients/` - ингредиенты

## Администрирование

**Данные администратора:**
- Email: admin@example.com
- Пароль: admin123

**Админ-панель:** `/admin/`

## SSL/HTTPS

Для настройки SSL на сервере:

```bash
# 1. Получить сертификат
sudo certbot certonly --standalone -d yourdomain.com

# 2. Активировать HTTPS
cd ~/foodgram/infra
sed -i 's/nginx.simple.conf/nginx.prod.conf/' docker-compose.prod.yml
docker-compose restart nginx
```

## Автор

[chacovoy](https://github.com/chacovoy)