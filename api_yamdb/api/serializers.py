
from rest_framework import serializers
from django.core.exceptions import ValidationError
from collections import OrderedDict

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

    username = serializers.CharField(validators=[])
    email = serializers.EmailField(validators=[])

    def validate(self, attrs):
        if attrs['username'] == 'me':
            raise serializers.ValidationError({"cannot create user me"})
        return super().validate(attrs)

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
        if User.objects.filter(username=data['username']).exists():
            user_obj = User.objects.get(username=data['username'])
            if user_obj.confirmation_code == data['confirmation_code']:
                return data
            else:
                raise ValidationError('Confirmation code is incorrect')
        raise ValidationError('User does not exist')

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.TimeField(required=False)
    last_name = serializers.TimeField(required=False)
    bio = serializers.TimeField(required=False)
    role = serializers.TimeField(required=False)

    def to_representation(self, instance):
        result = super(UserSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
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
