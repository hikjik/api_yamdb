from datetime import datetime

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, ValidationError

from api.fields import CurrentTitleDefault
from reviews.models import Category, Comment, Genre, Review, Title, User


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
        many=True, slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        fields = (
            'id',
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
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(
        choices=['user', 'admin', 'moderator'],
        required=False,
    )

    def to_representation(self, instance):
        my_fields = {'first_name', 'last_name', 'bio', 'role'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        model = User


class MeSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(
        choices=['user', 'admin', 'moderator'],
        required=False,
        read_only=True,
    )
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    def to_representation(self, instance):
        my_fields = {'first_name', 'last_name', 'bio', 'role'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        model = User


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True,
    )
    title = serializers.HiddenField(
        default=CurrentTitleDefault(),
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
                message="Запрещено оставлять отзыв на одно произведение дважды"
            ),
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True,
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
