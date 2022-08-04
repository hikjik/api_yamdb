from django.contrib import admin

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)

admin.site.register([
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User,
])
