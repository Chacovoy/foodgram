import secrets

from django.contrib.auth import get_user_model, update_session_auth_hash
from django.db.models import F, Sum
from django.http import HttpResponse

from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram.constants import SHORT_CODE_LENGTH
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    ShortLink,
    Tag,
)
from users.models import Subscription
from .fields import Base64ImageField
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnlyPermission
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    RecipeShortSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserGetSerializer,
    UserPostSerializer,
    UserWithRecipesSerializer,
)
from .utils import create_related_object, delete_related_object

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_instance(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action in ['subscriptions', 'subscribe']:
            return UserWithRecipesSerializer
        elif self.request.method == 'GET':
            return UserGetSerializer
        return UserPostSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        instance = self.get_instance()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            update_session_auth_hash(request, self.request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(following__user=user)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        return create_related_object(
            self,
            request,
            User,
            Subscription,
            SubscriptionSerializer,
            **kwargs
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        return delete_related_object(
            request,
            User,
            Subscription,
            **kwargs
        )

    @action(
        detail=False,
        methods=['PUT'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user

        if 'avatar' not in request.data:
            return Response(
                {'avatar': ['Это поле обязательно.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        avatar_field = Base64ImageField()
        avatar_data = avatar_field.to_internal_value(request.data['avatar'])
        user.avatar = avatar_data
        user.save()
        serializer = UserGetSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user

        if not user.avatar:
            return Response(
                {'error': 'Аватар не установлен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.avatar.delete(save=False)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnlyPermission]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        elif self.action in ['favorite', 'shopping_cart', ]:
            return RecipeShortSerializer

        return RecipePostSerializer

    @action(
        methods=['POST'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, **kwargs):
        return create_related_object(
            self,
            request,
            Recipe,
            Favorite,
            FavoriteSerializer,
            **kwargs
        )

    @favorite.mapping.delete
    def remove_favorite(self, request, **kwargs):
        return delete_related_object(
            request,
            Recipe,
            Favorite,
            **kwargs
        )

    @action(
        methods=['POST'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, **kwargs):
        return create_related_object(
            self,
            request,
            Recipe,
            ShoppingCart,
            ShoppingCartSerializer,
            **kwargs
        )

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, **kwargs):
        return delete_related_object(
            request,
            Recipe,
            ShoppingCart,
            **kwargs
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shoppingcart_set__user=user
        ).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount'))
        data = []
        for ingredient in ingredients:
            data.append(
                f'{ingredient["name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["measurement_unit"]}'
            )
        content = 'Список покупок:\n\n' + '\n'.join(data)
        filename = 'Shopping_cart.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=[],
        url_path='get-link'
    )
    def get_link(self, request, **kwargs):
        recipe = self.get_object()

        short_link, created = ShortLink.objects.get_or_create(
            recipe=recipe,
            defaults={'short_code': secrets.token_urlsafe(SHORT_CODE_LENGTH)}
        )

        link = (f"{request.scheme}://{request.get_host()}"
                f"/s/{short_link.short_code}/")
        return Response({'short-link': link})
