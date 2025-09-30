from rest_framework import serializers

from recipes.models import Favorite, ShoppingCart
from users.models import Subscription


def get_recipe_user_unique_validator(model, message):
    return serializers.UniqueTogetherValidator(
        queryset=model.objects.all(),
        fields=['recipe', 'user'],
        message=message
    )


def get_subscription_unique_validator():
    return serializers.UniqueTogetherValidator(
        queryset=Subscription.objects.all(),
        fields=['author', 'user'],
        message="Вы уже подписаны на этого пользователя"
    )


def get_favorite_unique_validator():
    return get_recipe_user_unique_validator(
        Favorite,
        'Этот рецепт уже добавлен в избранное.'
    )


def get_shopping_cart_unique_validator():
    return get_recipe_user_unique_validator(
        ShoppingCart,
        'Этот рецепт уже добавлен в список покупок.'
    )
