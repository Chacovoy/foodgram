from django.contrib.auth import get_user_model, update_session_auth_hash
from django.db.models import F, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from djoser.serializers import SetPasswordSerializer

from recipes.models import (Favorite, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscription
from .filters import IngredientFilter, RecipeFilter
from .helpers import process_base64_avatar
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          RecipeShortSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserGetSerializer, UserPostSerializer,
                          UserWithRecipesSerializer)
from .utils import post_and_delete_action

User = get_user_model()


class CustomUserViewSet(
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
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        if request.method == 'GET':
            instance = self.get_instance()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=[IsAuthenticated, ]
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            update_session_auth_hash(request, self.request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated, ]
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
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated, ]
    )
    def subscribe(self, request, **kwargs):
        return post_and_delete_action(
            self,
            request,
            User,
            Subscription,
            SubscriptionSerializer,
            **kwargs
        )

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        url_name='me_avatar'
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            if 'avatar' in request.data:
                avatar_data = request.data['avatar']
                user.avatar = process_base64_avatar(avatar_data)

                user.save()
                serializer = UserGetSerializer(user,
                                               context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(
                {'avatar': ['Это поле обязательно.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            if 'avatar' in request.data:
                user.avatar = request.data['avatar']
                user.save()
                serializer = UserGetSerializer(user,
                                               context={'request': request})
                return Response(serializer.data)
            return Response(
                {'error': 'Аватар не предоставлен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Аватар не установлен'},
                status=status.HTTP_400_BAD_REQUEST
            )


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
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        elif self.action in ['favorite', 'shopping_cart', ]:
            return RecipeShortSerializer

        return RecipePostSerializer

    @action(["POST", "DELETE"], detail=True)
    def favorite(self, request, **kwargs):
        return post_and_delete_action(
            self,
            request,
            Recipe,
            Favorite,
            FavoriteSerializer,
            **kwargs
        )

    @action(["POST", "DELETE"], detail=True)
    def shopping_cart(self, request, **kwargs):
        return post_and_delete_action(
            self,
            request,
            Recipe,
            ShoppingCart,
            ShoppingCartSerializer,
            **kwargs
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount')
        )
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
        link = (f"{request.scheme}://{request.get_host()}"
                f"/recipes/{recipe.id}/")
        return Response({'short-link': link})


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def avatar_upload(request):
    user = request.user

    if 'avatar' in request.data:
        avatar_data = request.data['avatar']
        user.avatar = process_base64_avatar(avatar_data)

        user.save()
        serializer = UserGetSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(
        {'avatar': ['Это поле обязательно.']},
        status=status.HTTP_400_BAD_REQUEST
    )
