
import hashlib
from datetime import datetime

from api.filters import TitleFilters
from api.permissions import (IsAdminOrModeratorOrAuthorOrReadOnly,
                             IsAdminOrReadOnly, IsAdminPermission)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleGetSerializer, TitlePostSerializer,
                             UserGetTokenSerializer, UserSerializer,
                             UserSingUpSerializer)
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User


def send_confirmation_code(data):
    username = data['username']
    email = data['email']

    timestamp = datetime.now().timestamp()
    string_to_hash = username + email + str(timestamp)
    confirmation_code = hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()

    send_mail(
        'Verification Code',
        'Hello {}. Your confirmation code is: {}'.format(
            username,
            confirmation_code),
        'from@example.com',
        [email],
        fail_silently=False,
    )
    user_obj = User.objects.filter(username=username)
    user_obj.update(confirmation_code=confirmation_code)
    return confirmation_code


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    return token


class UserSignUp(APIView):

    def post(self, request):
        serializer_1 = UserSingUpSerializer(data=request.data)
        if serializer_1.is_valid():
            username = request.data['username']
            email = request.data['email']
            if User.objects.filter(username=username, email=email).exists():
                send_confirmation_code(request.data)
                return Response(serializer_1.data)
            else:
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    send_confirmation_code(request.data)
                    return Response(serializer_1.data)
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer_1.errors, status=status.HTTP_400_BAD_REQUEST
        )


class UserGetToken(APIView):
    def post(self, request):
        serializer = UserGetTokenSerializer(data=request.data)
        if serializer.is_valid():
            jwt_token = get_tokens_for_user(
                User.objects.get(username=request.data['username']))
            return Response({'token': jwt_token})
        else:
            if 'non_field_errors' in serializer._errors:
                if serializer._errors['non_field_errors'][0] == 'User does not exist':
                    return Response(
                        serializer.errors, status=status.HTTP_404_NOT_FOUND
                    )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminPermission,)
    lookup_field = 'username'

    def retrieve(self, request, *args, **kwargs):
        if kwargs.get('username') == 'me':
            return Response(self.get_serializer(request.user).data)
        return super().retrieve(request, args, kwargs)

    def perform_create(self, serializer):
        serializer.save()


class ListCreateDestroyViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    pass


class CategoryViewSet(
    ListCreateDestroyViewSet
):
    queryset = Category.objects.all()
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(
    ListCreateDestroyViewSet
):
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilters

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminOrModeratorOrAuthorOrReadOnly,
    ]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminOrModeratorOrAuthorOrReadOnly,
    ]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )
        serializer.save(author=self.request.user, review=review)
