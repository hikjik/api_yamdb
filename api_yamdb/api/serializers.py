from datetime import datetime

from rest_framework import serializers
from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'name',
            'slug'
        )
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'name',
            'slug'
        )
        model = Genre


class TitlePostSerializer(serializers.ModelSerializer):
    description = serializers.IntegerField(required=False)
    genre = serializers.SlugRelatedField(
        many=True, slug_field='name',
        queryset=Genre.objects.all()
    )

    class Meta:
        fields = (
            'name',
            'year',
            'description',
            'genre',
            'category'
        )
        model = Title

        def validate_year(self, value):
            if value > datetime.now().year:
                raise serializers.ValidationError(
                    'Нельзя добавлять произведения, которые еще не вышли'
                )
            return value


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    description = serializers.StringRelatedField(
        required=False, read_only=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        model = Title
