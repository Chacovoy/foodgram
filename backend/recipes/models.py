from django.db import models
from django.db.models import UniqueConstraint

from foodgram.constants import (HEX_COLOR_MAX_LENGTH, INGREDIENT_UNIT_MAX_LENGTH,
                                RECIPE_NAME_MAX_LENGTH, TAG_NAME_MAX_LENGTH)
from users.models import User
from .validators import (hex_color_validator, min_cooking_time_validator,
                         min_ingredient_amount_validator, name_validator)


class Ingredient(models.Model):
    name = models.CharField(
        'Наименование ингредиента',
        max_length=RECIPE_NAME_MAX_LENGTH,
        validators=[name_validator]
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=INGREDIENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} в {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Тэг',
        unique=True,
        max_length=TAG_NAME_MAX_LENGTH,
        validators=[name_validator]
    )
    slug = models.SlugField(unique=True, db_index=True)
    color = models.CharField(
        'Цвет тэга в HEX формате',
        max_length=HEX_COLOR_MAX_LENGTH,
        validators=[hex_color_validator]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        'Название рецепта',
        max_length=RECIPE_NAME_MAX_LENGTH,
        validators=[name_validator]
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    cooking_time = models.IntegerField(
        'Время приготовления в минутах',
        validators=[min_cooking_time_validator]
    )
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='IngredientsInRecipe',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='IngredientsInRecipe',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        'Колличество ингредиента в данном рецепте.',
        validators=[min_ingredient_amount_validator]
    )

    class Meta:
        verbose_name = 'Ингридиент в рецепте '
        verbose_name_plural = 'Ингридиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient.name} в рецепте {self.recipe.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='FavoriteRecipe',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='FavoriteRecipe',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.recipe.name} в списке избанного у {self.user.username}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='RecipeInShoppingList',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.recipe.name} в списке покупок у {self.user.username}'
