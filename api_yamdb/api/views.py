
import hashlib
from datetime import datetime
from django.http import Http404

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter


from reviews.models import Category, Genre, Title, Review, User
from api.serializers import (
    UserSingUpSerializer,
    UserGetTokenSerializer,
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
)
from api.permissions import (
    IsAdminOrModeratorOrAuthorOrReadOnly,
    IsAdminPermission,
    IsAdminOrReadOnly
)


def send_confirmation_code(username, email):
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
    return {
        'access': str(refresh.access_token),
    }


class UserSignUp(APIView):

    def post(self, request):
        serializer = UserSingUpSerializer(data=request.data)
        if serializer.is_valid():
            username = request.data['username']
            email = request.data['email']
            if User.objects.filter(username = username).exists():
                send_confirmation_code(
                    username,
                    email
                )
            else:
                serializer.save()
                send_confirmation_code(
                    username,
                    email
                )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserGetToken(APIView):
    def post(self, request):
        serializer = UserGetTokenSerializer(data=request.data)
        if serializer.is_valid():
            jwt_token = get_tokens_for_user(
                User.objects.get(username=request.data['username']))
            return Response({'token': jwt_token})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = (IsAdminPermission,)


    def perform_create(self, serializer):
        serializer.save()

    # def destroy(self, request, *args, **kwargs):


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly, IsAuthenticatedOrReadOnly]
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly, IsAuthenticatedOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly, IsAuthenticatedOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category', 'genre', 'name', 'year',)


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
