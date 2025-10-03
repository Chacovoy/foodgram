EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 150
USERNAME_MAX_LENGTH = 150
RECIPE_NAME_MAX_LENGTH = 256
INGREDIENT_NAME_MAX_LENGTH = 128
TAG_NAME_MAX_LENGTH = 32
TAG_SLUG_MAX_LENGTH = 32
INGREDIENT_UNIT_MAX_LENGTH = 64
SHORT_CODE_MAX_LENGTH = 10

MIN_COOKING_TIME = 1
MIN_INGREDIENT_AMOUNT = 1
MIN_VALUE_ZERO = 0

SHORT_CODE_LENGTH = 6

PAGE_SIZE = 6
PAGE_SIZE_QUERY_PARAM = 'limit'

NAME_REGEX = r'^[а-яА-ЯёЁa-zA-Z -]+$'

CHOICES_LIST = (
    ('0', 'False'),
    ('1', 'True')
)

INVALID_NAME_MESSAGE = 'Введите корректное имя/название'
MIN_COOKING_TIME_MESSAGE = 'Время приготовление должно быть не менее минуты'
MIN_INGREDIENT_AMOUNT_MESSAGE = (
    'Колличество ингредиента в рецепте не должно быть менее 1.'
)
INVALID_USERNAME_MESSAGE = 'Имя пользователя не может быть "me"'
