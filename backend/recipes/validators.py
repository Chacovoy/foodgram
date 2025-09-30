from django.core.validators import MinValueValidator, RegexValidator

from foodgram.constants import (INVALID_NAME_MESSAGE, MIN_COOKING_TIME,
                                MIN_COOKING_TIME_MESSAGE, MIN_INGREDIENT_AMOUNT,
                                MIN_INGREDIENT_AMOUNT_MESSAGE, NAME_REGEX)


name_validator = RegexValidator(
    regex=NAME_REGEX,
    message=INVALID_NAME_MESSAGE
)

# Валидатор для минимального времени приготовления
min_cooking_time_validator = MinValueValidator(
    MIN_COOKING_TIME, MIN_COOKING_TIME_MESSAGE
)

# Валидатор для минимального количества ингредиента
min_ingredient_amount_validator = MinValueValidator(
    MIN_INGREDIENT_AMOUNT, MIN_INGREDIENT_AMOUNT_MESSAGE
)
