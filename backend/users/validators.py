from django.core.exceptions import ValidationError

from foodgram.constants import INVALID_USERNAME_MESSAGE


def check_username(value):
    if value.lower() == 'me':
        raise ValidationError(INVALID_USERNAME_MESSAGE)
