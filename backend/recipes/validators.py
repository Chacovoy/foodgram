from django.core.validators import MinValueValidator

from foodgram.constants import (
    MIN_COOKING_TIME,
    MIN_COOKING_TIME_MESSAGE,
    MIN_INGREDIENT_AMOUNT,
    MIN_INGREDIENT_AMOUNT_MESSAGE,
)


min_cooking_time_validator = MinValueValidator(
    MIN_COOKING_TIME, MIN_COOKING_TIME_MESSAGE
)

min_ingredient_amount_validator = MinValueValidator(
    MIN_INGREDIENT_AMOUNT, MIN_INGREDIENT_AMOUNT_MESSAGE
)
