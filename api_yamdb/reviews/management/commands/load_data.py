import csv
import os
import stat

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import User, Category, Genre, Title, GenreTitle, Review, Comment

TABLES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    GenreTitle: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model, filename in TABLES.items():
            path = os.path.join(
                settings.BASE_DIR, "static", "data", filename)
            with open(path, 'r', encoding='utf-8') as csvfile:
                for row in csv.DictReader(csvfile):
                    model(**self._fix_names(row)).save()
            self.stdout.write(
                self.style.SUCCESS(f"Загружены данные из файла '{filename}'."))

    @staticmethod
    def _fix_names(dct):
        NAMES = {'author', 'category', 'title', 'review'}
        return {f'{k}_id' if k in NAMES else k: v for k, v in dct.items()}
