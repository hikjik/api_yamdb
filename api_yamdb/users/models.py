from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

    ROLES = [
        (USER, "Пользователь"),
        (ADMIN, "Администратор"),
        (MODERATOR, "Модератор"),
    ]

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="Адрес электронной почты",
    )
    role = models.CharField(
        max_length=16,
        choices=ROLES,
        default=USER,
        verbose_name="Роль пользователя",
    )
    bio = models.TextField(
        max_length=1024,
        blank=True,
        verbose_name="Биография пользователя",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def is_admin(self):
        return self.role == User.ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    def __str__(self):
        return self.username
