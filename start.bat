@echo off
echo Запуск Foodgram...

cd /d "%~dp0\infra"

echo Остановка старых контейнеров...
docker-compose down

echo Запуск новых контейнеров...
docker-compose up --build -d

echo.
echo Приложение запущено!
echo Фронтенд: http://localhost
echo API: http://localhost/api/
echo Админка: http://localhost/admin/
echo.
echo Логи: docker-compose logs -f
echo Остановка: docker-compose down
echo.
pause
