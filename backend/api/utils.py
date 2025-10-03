from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe

User = get_user_model()


def create_related_object(
        self, request, model, related_model, serializer_class, **kwargs
):
    obj = get_object_or_404(model, id=kwargs['pk'])
    data = request.data.copy()

    if model == Recipe:
        data.update({'recipe': obj.id})
    elif model == User:
        data.update({'author': obj.id})

    serializer = serializer_class(data=data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(
        status=status.HTTP_201_CREATED,
        data=self.get_serializer(obj).data
    )


def delete_related_object(request, model, related_model, **kwargs):
    obj = get_object_or_404(model, id=kwargs['pk'])

    if model == Recipe:
        related_obj = related_model.objects.filter(
            recipe=obj,
            user=request.user
        )
        error_message = 'В списке покупок(в избранном) нет этого рецепта.'
    elif model == User:
        related_obj = related_model.objects.filter(
            author=obj,
            user=request.user
        )
        error_message = 'Вы не подписаны на этого пользователя'

    deleted_count, _ = related_obj.delete()

    if deleted_count == 0:
        return Response(
            {'errors': error_message},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(status=status.HTTP_204_NO_CONTENT)
