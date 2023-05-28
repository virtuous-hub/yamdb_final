from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    USER_ROLES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь')
    )
    email = models.EmailField(

        max_length=254,
        verbose_name='Адрес электронной почты'
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True
    )
    confirmation_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        editable=False,
        unique=True)
    bio = models.TextField(
        'Биография',
        blank=True,
        null=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=30,
        choices=USER_ROLES,
        default='user'
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR or self.is_staff
