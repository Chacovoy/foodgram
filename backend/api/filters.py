from distutils.util import strtobool

from django_filters import rest_framework

from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart
from .constants import CHOICES_LIST


class IngredientFilter(rest_framework.FilterSet):
    """Фильтр для ингредиентов."""
    name = rest_framework.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(rest_framework.FilterSet):
    """Фильтр для рецептов: по избранному, списку покупок, автору и тагам."""
    is_favorited = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_favorited_method'
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_in_shopping_cart_method'
    )
    author = rest_framework.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        conjoined=False,  # Использовать OR вместо AND для множественных тегов
        method='filter_tags'
    )

    def is_favorited_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        favorites = Favorite.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in favorites]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    def is_in_shopping_cart_method(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    def filter_tags(self, queryset, name, value):
        """
        Фильтрация по тегам с поддержкой множественных параметров.
        
        Поддерживает: ?tags=breakfast&tags=dinner и ?tags=breakfast,dinner
        """
        if not value:
            return queryset
            
        tag_slugs = []
        
        # Если value - это список (множественные параметры ?tags=a&tags=b)
        if isinstance(value, list):
            for item in value:
                if hasattr(item, 'slug'):  # Это объект Tag
                    tag_slugs.append(item.slug)
                else:  # Это строка
                    tag_slugs.append(str(item))
        else:
            # Если value - строка, разделяем по запятым (?tags=a,b)
            if isinstance(value, str) and ',' in value:
                tag_slugs = [slug.strip() for slug in value.split(',')]
            else:
                # Одиночное значение
                if hasattr(value, 'slug'):
                    tag_slugs = [value.slug]
                else:
                    tag_slugs = [str(value)]
        
        # Фильтруем рецепты, которые имеют любой из указанных тегов
        return queryset.filter(tags__slug__in=tag_slugs).distinct()

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
