# Константы для полей моделей

# Максимальные длины полей (согласно OpenAPI спецификации)
EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 150  # Для имен, фамилий пользователей
RECIPE_NAME_MAX_LENGTH = 256  # Для названий рецептов (OpenAPI: maxLength 256)
INGREDIENT_NAME_MAX_LENGTH = 128  # Для названий ингредиентов
TAG_NAME_MAX_LENGTH = 32  # Для названий тегов (OpenAPI: maxLength 32)
TAG_SLUG_MAX_LENGTH = 32  # Для slug тегов (OpenAPI: maxLength 32)
INGREDIENT_UNIT_MAX_LENGTH = 64  # Для единиц измерения (OpenAPI: maxLength 64)

# Минимальные значения
MIN_COOKING_TIME = 1  # Минимальное время приготовления в минутах
MIN_INGREDIENT_AMOUNT = 1  # Минимальное количество ингредиента

# Регулярные выражения
NAME_REGEX = r'^[а-яА-ЯёЁa-zA-Z -]+$'  # Для имен и названий

# Сообщения валидаторов
INVALID_NAME_MESSAGE = 'Введите корректное имя/название'
MIN_COOKING_TIME_MESSAGE = 'Время приготовление должно быть не менее минуты'
MIN_INGREDIENT_AMOUNT_MESSAGE = (
    'Колличество ингредиента в рецепте не должно быть менее 1.'
)
INVALID_USERNAME_MESSAGE = 'Имя пользователя не может быть "me"'
