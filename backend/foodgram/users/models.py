from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

USER = 'user'
ADMIN = 'admin'
ROLES = (
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Допустимые символы: буквы, цифры, +, @, ., -,_')],
        verbose_name='Уникальное имя',
        help_text='Введите имя пользователя',
    )
    email = models.EmailField(
        db_index=True,
        unique=True,
        max_length=254,
        verbose_name='Электронная почта',
        help_text='Введите адрес электронной почты',
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Имя',
        help_text='Введите имя пользователя',
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Фамилия',
        help_text='Введите фамилию пользователя',
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        help_text='Введите пароль',
    )
    role = models.CharField(
        max_length=16,
        choices=ROLES,
        default=USER,
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name='Подписка на данного пользователя',
        help_text='Подписаться',
    )

    class Meta:
        ordering = ('role', )

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser or self.role == self.ADMIN

    def __str__(self):
        return self.username
