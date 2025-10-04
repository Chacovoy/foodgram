from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response


def create_related_object(
    self, request, model,
    serializer_class, response_serializer_class, field_name, **kwargs
):
    obj = get_object_or_404(model, id=kwargs['pk'])

    serializer = serializer_class(
        data={field_name: obj.id},
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    response_serializer = response_serializer_class(
        obj,
        context={'request': request}
    )
    return Response(
        status=status.HTTP_201_CREATED,
        data=response_serializer.data
    )


def delete_related_object(
    request, model, related_model, field_name, **kwargs
):
    obj = get_object_or_404(model, id=kwargs['pk'])

    deleted_count, _ = related_model.objects.filter(
        user=request.user,
        **{field_name: obj}
    ).delete()

    if deleted_count == 0:
        return Response(
            {'errors': 'Объект не найден.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(status=status.HTTP_204_NO_CONTENT)
