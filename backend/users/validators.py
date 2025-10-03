from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from foodgram.constants import (
    INVALID_NAME_MESSAGE,
    INVALID_USERNAME_MESSAGE,
    NAME_REGEX,
)


def check_username(value):
    if value.lower() == 'me':
        raise ValidationError(INVALID_USERNAME_MESSAGE)


user_name_validator = RegexValidator(
    regex=NAME_REGEX,
    message=INVALID_NAME_MESSAGE
)


def get_user_name_validators():
    return [user_name_validator, check_username]


def get_username_validators():
    return [check_username]
