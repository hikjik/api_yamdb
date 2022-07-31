from rest_framework import serializers
from django.core.exceptions import ValidationError

from reviews.models import Category, Genre, Title, Review, Comment, User


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


class UserSingUpSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email')
        model = User


class UserGetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[])
    confirmation_code = serializers.CharField(validators=[])

    class Meta:
        fields = ('username', 'confirmation_code', )
        model = User

    def validate(self, data):
        print(data)
        user_obj = User.objects.get(username=data['username'])
        if user_obj.confirmation_code == data['confirmation_code']:
            return data
        else:
            raise ValidationError('Confirmation code is incorrect')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email', 'role')
        model = User


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
