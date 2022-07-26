from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class User(AbstractUser):
    #    username
    #    email
    #    role (choices одно из трех: user, admin, moderator)
    #    bio
    #    first_name
    #    last_name
    pass


class Category(models.Model):
    #    name
    #    slug
    pass


class Genre(models.Model):
    #    name
    #    slug
    pass


class Title(models.Model):
    #    name
    #    year
    #    category ForeignKey
    #    ...
    pass


class GenreTitle(models.Model):
    #    genre ForeignKey
    #    title ForeignKey
    pass


class Review(models.Model):
    text = models.TextField(verbose_name='Текст отзыва')
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Оценка должна быть >= 1'),
            MaxValueValidator(10, 'Оценка должна быть <= 10'),
        ],
        verbose_name='Оценка произведения',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации отзыва',
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    rewiew = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
