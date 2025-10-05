from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from foodgram.constants import MIN_INGREDIENT_AMOUNT, MIN_VALUE_ZERO
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Subscription
from .fields import Base64ImageField

User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            not request.user.is_anonymous
            and Subscription.objects.filter(
                author=obj, user=request.user
            ).exists()
        )


class UserWithRecipesSerializer(UserGetSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserGetSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, object):
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = object.recipes.all()
        if recipe_limit:
            try:
                limit = int(recipe_limit)
                if limit > MIN_VALUE_ZERO:
                    queryset = queryset[:limit]
            except (ValueError, TypeError):
                pass

        return RecipeShortSerializer(queryset, context=context, many=True).data


class UserPostSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть "me"'
            )
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Subscription
        fields = ('author', 'user')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['author', 'user'],
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate_author(self, value):
        if self.context.get('request').user == value:
            raise serializers.ValidationError(
                'Подписка на самого себя не возможна!'
            )
        return value

    def to_representation(self, instance):
        return UserWithRecipesSerializer(
            instance.author,
            context=self.context
        ).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserGetSerializer()
    ingredients = IngredientInRecipeSerializer(
        source='IngredientsInRecipe',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            not request.user.is_anonymous
            and Favorite.objects.filter(
                recipe=obj, user=request.user
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            not request.user.is_anonymous
            and ShoppingCart.objects.filter(
                recipe=obj, user=request.user
            ).exists()
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserGetSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    @staticmethod
    def save_ingredients(recipe, ingredients):
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        )

    def validate(self, data):
        cooking_time = data.get('cooking_time')
        if cooking_time <= MIN_VALUE_ZERO:
            raise serializers.ValidationError(
                {
                    'error': 'Время приготовления не должно быть менее 1 мин.'
                }
            )
        ingredients_list = []
        ingredients_in_recipe = data.get('ingredients')
        for ingredient in ingredients_in_recipe:
            ingredients_list.append(ingredient['id'])
        if len(ingredients_list) > len(set(ingredients_list)):
            raise serializers.ValidationError(
                {
                    'error': 'Ингредиенты в рецепте не должны повторяться.'
                }
            )
        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)
        self.save_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance = super().update(instance, validated_data)

        instance.tags.set(tags)
        instance.ingredients.clear()
        self.save_ingredients(instance, ingredients)

        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['recipe', 'user'],
                message='Этот рецепт уже добавлен в избранное.'
            )
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['recipe', 'user'],
                message='Этот рецепт уже добавлен в список покупок.'
            )
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context=self.context
        ).data
