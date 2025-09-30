from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from .validators import check_username


class User(AbstractUser):
    """Кастомная модель пользователя.
    Поля email, first_name и last_name обязательны,
    уникальный идентификатор - email.
    """

    email = models.EmailField(
        'email',
        max_length=254,
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^[а-яА-ЯёЁa-zA-Z -]+$',
                message='Введите корректное имя/название'
            ), check_username
        ]
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^[а-яА-ЯёЁa-zA-Z -]+$',
                message='Введите корректное имя/название'
            ), check_username
        ]
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
    )

    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'last_name', 'first_name', ]

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Подписки на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор, на которого подписываются',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_subscription')
        ]
