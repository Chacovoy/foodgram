# Инструкция по настройке автоматического деплоя

## 1. Настройка Docker Hub

### Создание аккаунта и репозиториев:
1. Зарегистрируйтесь на [Docker Hub](https://hub.docker.com/)
2. Создайте публичные репозитории:
   - `your-username/foodgram_backend`
   - `your-username/foodgram_frontend`

### Сборка и push образов:
```bash
# Войдите в Docker Hub
docker login

# Соберите и загрузите backend образ
docker build -t your-username/foodgram_backend:latest ./backend/
docker push your-username/foodgram_backend:latest

# Соберите и загрузите frontend образ
docker build -t your-username/foodgram_frontend:latest ./frontend/
docker push your-username/foodgram_frontend:latest
```

## 2. Настройка GitHub Secrets

В настройках репозитория GitHub (Settings → Secrets and variables → Actions) добавьте:

### Docker Hub секреты:
- `DOCKER_USERNAME` - ваш username в Docker Hub
- `DOCKER_PASSWORD` - ваш password или access token

### Сервер секреты:
- `HOST` - IP адрес вашего сервера (например: 51.250.1.100)
- `USERNAME` - имя пользователя на сервере (например: ubuntu)
- `SSH_KEY` - приватный SSH ключ для доступа к серверу

## 3. Настройка сервера

### Установка Docker и Docker Compose:
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагрузка для применения изменений групп
sudo reboot
```

### Клонирование проекта:
```bash
# Клонируйте ваш репозиторий
git clone https://github.com/your-username/foodgram-main.git
cd foodgram-main/infra
```

### Обновление docker-compose.yml:
Замените секции сборки на использование образов из Docker Hub:

```yaml
backend:
  container_name: foodgram-backend
  image: your-username/foodgram_backend:latest  # Вместо build: ../backend
  environment:
    # ... остальные переменные

frontend:
  container_name: foodgram-front
  image: your-username/foodgram_frontend:latest  # Вместо build: ../frontend
```

## 4. Запуск проекта

### Первый запуск:
```bash
cd /home/your-username/foodgram-main/infra
docker-compose up -d
```

### Проверка статуса:
```bash
docker-compose ps
docker-compose logs -f
```

## 5. Проверка работы

После успешного деплоя:
1. Откройте браузер и перейдите по IP адресу сервера
2. Проверьте, что фронтенд загружается
3. Проверьте API по адресу `http://your-server-ip/api/`
4. Проверьте документацию API по адресу `http://your-server-ip/api/docs/`

## 6. Автоматический деплой

После настройки всех секретов, при каждом push в ветку main/master:
1. GitHub Actions автоматически соберет новые образы
2. Загрузит их в Docker Hub
3. Подключится к серверу
4. Обновит и перезапустит контейнеры

## 7. Мониторинг и логи

### Просмотр логов:
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### Мониторинг ресурсов:
```bash
# Использование ресурсов контейнерами
docker stats

# Общая информация о Docker
docker system df
```

## 8. Резервное копирование

### Backup базы данных:
```bash
# Создание backup
docker-compose exec db pg_dump -U foodgram_user foodgram_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из backup
docker-compose exec -T db psql -U foodgram_user foodgram_db < backup_file.sql
```

### Backup медиа файлов:
```bash
# Копирование медиа файлов
docker cp foodgram-backend:/app/media ./media_backup_$(date +%Y%m%d_%H%M%S)
```
