# Константы для полей моделей

# Максимальные длины полей
EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 150  # Для имен, фамилий, паролей пользователей
RECIPE_NAME_MAX_LENGTH = 200  # Для названий рецептов и ингредиентов
TAG_NAME_MAX_LENGTH = 200  # Для названий тегов
INGREDIENT_UNIT_MAX_LENGTH = 100  # Для единиц измерения ингредиентов
HEX_COLOR_MAX_LENGTH = 7  # Для HEX цветов (#FFFFFF)

# Минимальные значения
MIN_COOKING_TIME = 1  # Минимальное время приготовления в минутах
MIN_INGREDIENT_AMOUNT = 1  # Минимальное количество ингредиента

# Регулярные выражения
NAME_REGEX = r'^[а-яА-ЯёЁa-zA-Z -]+$'  # Для имен и названий
HEX_COLOR_REGEX = r'^#([A-Fa-f0-9]{3,6})$'  # Для HEX цветов

# Сообщения валидаторов
INVALID_NAME_MESSAGE = 'Введите корректное имя/название'
INVALID_HEX_COLOR_MESSAGE = 'Введите значение цвета в формате HEX! Пример:#FF0000'
MIN_COOKING_TIME_MESSAGE = 'Время приготовление должно быть не менее минуты'
MIN_INGREDIENT_AMOUNT_MESSAGE = 'Колличество ингредиента в рецептне не должно быть менее 1.'
INVALID_USERNAME_MESSAGE = 'Имя пользователя не может быть "me"'
