# Foodgram - Проект запускаемый из контейнера

## Описание

Foodgram - это веб-приложение для публикации рецептов с возможностью подписки на авторов, добавления рецептов в избранное и составления списка покупок.

## Технологии

- **Backend**: Django 3.2, Django REST Framework, PostgreSQL
- **Frontend**: React.js
- **Контейнеризация**: Docker, Docker Compose
- **Веб-сервер**: Nginx

## Структура проекта

```
foodgram-main/
├── backend/                 # Django приложение
│   ├── api/                # API эндпоинты
│   ├── recipes/            # Модели рецептов
│   ├── users/              # Модели пользователей
│   ├── foodgram/           # Настройки Django
│   ├── data/               # CSV файлы с данными
│   └── Dockerfile          # Docker образ для бэкенда
├── frontend/               # React приложение
│   ├── src/                # Исходный код
│   └── Dockerfile          # Docker образ для фронтенда
├── infra/                  # Конфигурация Docker
│   ├── docker-compose.yml  # Оркестрация контейнеров
│   ├── nginx.conf          # Конфигурация Nginx
│   └── init_db.sh          # Скрипт инициализации БД
└── docs/                   # Документация API
```

## Быстрый запуск

### Предварительные требования

- Docker
- Docker Compose

### Запуск проекта

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd foodgram-main
```

2. Перейдите в папку infra и запустите контейнеры:
```bash
cd infra
docker-compose up --build
```

3. Проект будет доступен по адресу: http://localhost

### Доступ к админке

- URL: http://localhost/admin/
- Логин: `admin`
- Пароль: `admin123`

## API Endpoints

### Аутентификация
- `POST /api/auth/token/login/` - Вход в систему
- `POST /api/auth/token/logout/` - Выход из системы

### Пользователи
- `GET /api/users/` - Список пользователей
- `GET /api/users/me/` - Текущий пользователь
- `POST /api/users/` - Регистрация
- `POST /api/users/set_password/` - Смена пароля
- `PUT /api/users/me/avatar/` - Обновление аватара
- `DELETE /api/users/me/avatar/` - Удаление аватара
- `POST /api/users/reset_password/` - Сброс пароля
- `GET /api/users/subscriptions/` - Подписки
- `POST /api/users/{id}/subscribe/` - Подписка на автора
- `DELETE /api/users/{id}/subscribe/` - Отписка от автора

### Рецепты
- `GET /api/recipes/` - Список рецептов
- `POST /api/recipes/` - Создание рецепта
- `GET /api/recipes/{id}/` - Детали рецепта
- `PATCH /api/recipes/{id}/` - Обновление рецепта
- `DELETE /api/recipes/{id}/` - Удаление рецепта
- `POST /api/recipes/{id}/favorite/` - Добавить в избранное
- `DELETE /api/recipes/{id}/favorite/` - Удалить из избранного
- `POST /api/recipes/{id}/shopping_cart/` - Добавить в корзину
- `DELETE /api/recipes/{id}/shopping_cart/` - Удалить из корзины
- `GET /api/recipes/download_shopping_cart/` - Скачать список покупок
- `GET /api/recipes/{id}/get-link/` - Получить ссылку на рецепт

### Ингредиенты и теги
- `GET /api/ingredients/` - Список ингредиентов
- `GET /api/tags/` - Список тегов

## Переменные окружения

Проект использует следующие переменные окружения (настроены в docker-compose.yml):

- `SECRET_KEY` - Секретный ключ Django
- `DEBUG` - Режим отладки (True/False)
- `DB_ENGINE` - Движок базы данных
- `DB_NAME` - Имя базы данных
- `POSTGRES_USER` - Пользователь PostgreSQL
- `POSTGRES_PASSWORD` - Пароль PostgreSQL
- `DB_HOST` - Хост базы данных
- `DB_PORT` - Порт базы данных

## Структура базы данных

### Основные модели:
- **User** - Пользователи (кастомная модель)
- **Recipe** - Рецепты
- **Ingredient** - Ингредиенты
- **Tag** - Теги
- **IngredientInRecipe** - Связь рецептов и ингредиентов
- **Favorite** - Избранные рецепты
- **ShoppingCart** - Корзина покупок
- **Subscription** - Подписки на авторов

## Разработка

### Локальная разработка

Для разработки без Docker:

1. Установите зависимости:
```bash
cd backend
pip install -r requirements.txt
```

2. Настройте базу данных PostgreSQL

3. Примените миграции:
```bash
python manage.py migrate
```

4. Загрузите данные:
```bash
python manage.py load_ingredients_data
python manage.py load_tags_data
```

5. Запустите сервер:
```bash
python manage.py runserver
```

### Сборка фронтенда

```bash
cd frontend
npm install
npm run build
```

## Troubleshooting

### Проблемы с базой данных

Если возникают проблемы с подключением к базе данных:

1. Проверьте, что контейнер базы данных запущен:
```bash
docker-compose ps
```

2. Проверьте логи:
```bash
docker-compose logs db
docker-compose logs backend
```

### Проблемы с миграциями

Если нужно пересоздать базу данных:

```bash
docker-compose down -v
docker-compose up --build
```

### Проблемы с правами доступа

Если возникают проблемы с правами доступа к файлам:

```bash
sudo chown -R $USER:$USER .
```

## Лицензия

Проект создан в учебных целях.
