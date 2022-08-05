from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import validate_year
from users.models import User


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название категории",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Слаг категории",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название жанра",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Слаг жанра",
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название произведения",
    )
    year = models.PositiveSmallIntegerField(
        validators=[validate_year],
        db_index=True,
        verbose_name="Год публикации произведения",
    )
    genre = models.ManyToManyField(
        Genre,
        through="GenreTitle",
        verbose_name="Жанры произведения",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles",
        verbose_name="Категория произведения",
    )
    description = models.TextField(
        max_length=512,
        verbose_name="Описание произведения",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Жанр и произведение"
        verbose_name_plural = "Жанры и произведения"

    def __str__(self):
        return f"{self.genre} - {self.title}"


class Review(models.Model):
    text = models.TextField(
        verbose_name="Текст отзыва",
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор отзыва",
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, "Оценка должна быть >= 1"),
            MaxValueValidator(10, "Оценка должна быть <= 10"),
        ],
        verbose_name="Оценка произведения",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата публикации отзыва",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("title", "author"),
                name="unique_title_author",
            ),
        ]
        ordering = ["-pub_date"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.text[:20]


class Comment(models.Model):
    text = models.TextField(
        verbose_name="Текст комментария",
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата публикации комментария",
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text
