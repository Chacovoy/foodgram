from django_filters import rest_framework

from foodgram.constants import CHOICES_LIST
from recipes.models import Ingredient, Recipe, Tag


def check_filter_enabled(val):
    return val.lower() in ('y', 'yes', 't', 'true', 'on', '1')


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_favorited_method'
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_in_shopping_cart_method'
    )
    author = rest_framework.NumberFilter(field_name='author')
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def is_favorited_method(self, queryset, name, value):
        if self.request.user.is_authenticated and check_filter_enabled(value):
            return queryset.filter(favorite_set__user=self.request.user)
        return queryset

    def is_in_shopping_cart_method(self, queryset, name, value):
        if self.request.user.is_authenticated and check_filter_enabled(value):
            return queryset.filter(shoppingcart_set__user=self.request.user)
        return queryset
