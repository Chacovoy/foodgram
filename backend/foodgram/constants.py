EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 150
USERNAME_MAX_LENGTH = 150
RECIPE_NAME_MAX_LENGTH = 256
INGREDIENT_NAME_MAX_LENGTH = 128
TAG_NAME_MAX_LENGTH = 32
TAG_SLUG_MAX_LENGTH = 32
INGREDIENT_UNIT_MAX_LENGTH = 64

MIN_COOKING_TIME = 1
MIN_INGREDIENT_AMOUNT = 1

NAME_REGEX = r'^[а-яА-ЯёЁa-zA-Z -]+$'

INVALID_NAME_MESSAGE = 'Введите корректное имя/название'
MIN_COOKING_TIME_MESSAGE = 'Время приготовление должно быть не менее минуты'
MIN_INGREDIENT_AMOUNT_MESSAGE = (
    'Колличество ингредиента в рецепте не должно быть менее 1.'
)
INVALID_USERNAME_MESSAGE = 'Имя пользователя не может быть "me"'
