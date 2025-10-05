from django.shortcuts import redirect

from .models import ShortLink


def short_link_redirect(request, short_code):
    try:
        short_link = ShortLink.objects.get(short_code=short_code)
    except ShortLink.DoesNotExist:
        return redirect('/not_found/')
    return redirect(f'/recipes/{short_link.recipe.id}/')
