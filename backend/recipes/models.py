from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

from foodgram.constants import (
    INGREDIENT_NAME_MAX_LENGTH,
    INGREDIENT_UNIT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
)
from .validators import (
    min_cooking_time_validator,
    min_ingredient_amount_validator,
    name_validator,
)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Наименование ингредиента',
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        validators=[name_validator]
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=INGREDIENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_name_unit',
            ),
        ]

    def __str__(self):
        return f'{self.name} в {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Тэг',
        unique=True,
        max_length=TAG_NAME_MAX_LENGTH,
        validators=[name_validator]
    )
    slug = models.SlugField(unique=True, max_length=TAG_SLUG_MAX_LENGTH)

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
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.ingredient.name} в рецепте {self.recipe.name}'


class BaseUserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.recipe.name} у {self.user.username}'


class Favorite(BaseUserRecipe):
    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} в списке избранного у {self.user.username}'


class ShoppingCart(BaseUserRecipe):
    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart',
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} в списке покупок у {self.user.username}'


class ShortLink(models.Model):
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name='short_link',
        verbose_name='Рецепт'
    )
    short_code = models.CharField(
        'Короткий код',
        max_length=10,
        unique=True,
        db_index=True
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'

    def __str__(self):
        return f'{self.short_code} -> {self.recipe.name}'
