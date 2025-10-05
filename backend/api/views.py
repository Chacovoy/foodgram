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
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnlyPermission
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
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

    def get_queryset(self):
        if self.action == 'subscriptions':
            return User.objects.filter(following__user=self.request.user)
        return super().get_queryset()

    def get_object(self):
        if self.action == 'me':
            return self.request.user
        return super().get_object()

    def get_serializer_class(self):
        if self.action == 'subscriptions':
            return UserWithRecipesSerializer
        elif self.action in ['list', 'retrieve', 'me']:
            return UserGetSerializer
        return UserPostSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        return self.retrieve(request)

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
        return self.list(request)

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
            SubscriptionSerializer,
            'author',
            **kwargs
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        return delete_related_object(
            request,
            User,
            Subscription,
            'author',
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
        serializer = AvatarSerializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeGetSerializer
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
            FavoriteSerializer,
            'recipe',
            **kwargs
        )

    @favorite.mapping.delete
    def remove_favorite(self, request, **kwargs):
        return delete_related_object(
            request,
            Recipe,
            Favorite,
            'recipe',
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
            ShoppingCartSerializer,
            'recipe',
            **kwargs
        )

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, **kwargs):
        return delete_related_object(
            request,
            Recipe,
            ShoppingCart,
            'recipe',
            **kwargs
        )

    def generate_shopping_list(self, ingredients):
        return [
            f'{ingredient["name"]} - '
            f'{ingredient["amount"]} '
            f'{ingredient["measurement_unit"]}'
            for ingredient in ingredients
        ]

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

        shopping_list = self.generate_shopping_list(ingredients)
        content = 'Список покупок:\n\n' + '\n'.join(shopping_list)
        filename = 'Shopping_cart.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

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
