from datetime import datetime

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title, User

from api.fields import CurrentTitleDefault


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        model = User

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError(
                "Использовать имя 'me' в качестве username запрещено"
            )
        return value


class UserMeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ("role",)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Genre.objects.all(),
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )

    class Meta:
        fields = ("id", "name", "year", "description", "genre", "category")
        model = Title

        def validate_year(self, value):
            if value > datetime.now().year:
                raise serializers.ValidationError(
                    "Нельзя добавлять произведения, которые еще не вышли"
                )
            return value


class TitleReadOnlySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.rating

    class Meta:
        fields = ("id", "name", "year", "rating",
                  "description", "genre", "category")
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field="username",
        read_only=True,
    )
    title = serializers.HiddenField(
        default=CurrentTitleDefault(),
    )

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date", "title")
        model = Review
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=("author", "title"),
                message="Запрещено оставлять отзыв на одно произведение дважды",
            ),
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field="username",
        read_only=True,
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
