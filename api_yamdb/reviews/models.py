from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(models.Model):
    name = models.CharField(
        'название Категории',
        max_length=250
    )
    slug = models.SlugField(
        'слаг Группы',
        unique=True
    )

    def __str__(self):
        return self.title


class Genre(models.Model):
    name = models.CharField(
        'название жанра',
        max_length=250
    )
    slug = models.SlugField(
        'слаг жанра',
        unique=True
    )

    def __str__(self):
        return self.title


class Title(models.Model):
    name = models.CharField(
        'название произведения',
        max_length=250
    )
    year = models.IntegerField(
        'год публикации произведения',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='жанры произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='категория произведения'
    )
    description = models.TextField(
        'описание произведения',
        max_length=400
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    #    title ForeignKey
    #    text
    #    author
    #    score
    #    pub_date
    pass


class Comment(models.Model):
    #    review ForeignKey
    #    text
    #    author
    #    pub_date
    pass
