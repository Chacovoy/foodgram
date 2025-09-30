from django.core.validators import MinValueValidator, RegexValidator


# Валидатор для имен/названий (кириллица, латиница, пробелы, дефисы)
name_validator = RegexValidator(
    regex=r'^[а-яА-ЯёЁa-zA-Z -]+$',
    message='Введите корректное имя/название'
)

# Валидатор для HEX цвета
hex_color_validator = RegexValidator(
    regex=r'^#([A-Fa-f0-9]{3,6})$',
    message='Введите значение цвета в формате HEX! Пример:#FF0000'
)

# Валидатор для минимального времени приготовления
min_cooking_time_validator = MinValueValidator(
    1, 'Время приготовление должно быть не менее минуты'
)

# Валидатор для минимального количества ингредиента
min_ingredient_amount_validator = MinValueValidator(
    1, 'Колличество ингредиента в рецептне не должно быть менее 1.'
)
