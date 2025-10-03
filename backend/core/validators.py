from django.core.validators import RegexValidator

from foodgram.constants import INVALID_NAME_MESSAGE, NAME_REGEX


name_validator = RegexValidator(
    regex=NAME_REGEX,
    message=INVALID_NAME_MESSAGE
)
