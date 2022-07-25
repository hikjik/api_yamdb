from django.contrib.auth.models import AbstractUser
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
