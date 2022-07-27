from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__')
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
