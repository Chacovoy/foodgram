from django.core.exceptions import ValidationError

from core.validators import name_validator
from foodgram.constants import INVALID_USERNAME_MESSAGE


def check_username(value):
    if value.lower() == 'me':
        raise ValidationError(INVALID_USERNAME_MESSAGE)


def get_user_name_validators():
    return [name_validator, check_username]


def get_username_validators():
    return [check_username]
