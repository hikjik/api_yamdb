import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User


TABLES = {
    User: "users.csv",
    Category: "category.csv",
    Genre: "genre.csv",
    Title: "titles.csv",
    GenreTitle: "genre_title.csv",
    Review: "review.csv",
    Comment: "comments.csv",
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model, filename in TABLES.items():
            path = os.path.join(settings.BASE_DIR, "static", "data", filename)
            with open(path, "r", encoding="utf-8") as csv_file:
                for row in csv.DictReader(csv_file):
                    model(**self._fix_names(row)).save()
            self.stdout.write(
                self.style.SUCCESS(f"Загружены данные из файла '{filename}'.")
            )

    @staticmethod
    def _fix_names(dct):
        NAMES = {"author", "category", "title", "review"}
        return {f"{k}_id" if k in NAMES else k: v for k, v in dct.items()}
