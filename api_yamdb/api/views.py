from rest_framework.decorators import action
from django.db.models import Avg
from api.filters import TitleFilters
from api.permissions import (IsAdminOrModeratorOrAuthorOrReadOnly,
                             IsAdminOrReadOnly, IsAdminPermission,
                             IsUserAuthenticatedPermission)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleGetSerializer, TitlePostSerializer,
                             UserSingUpSerializer, UserGetTokenSerializer,
                             UserSerializer, MeSerializer)
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title, User


def send_confirmation_code(data):
    username = data['username']
    email = data['email']

    user = get_object_or_404(User, username=username)
    confirmation_code = default_token_generator.make_token(user)

    send_mail(
        'Verification Code',
        'Hello {}. Your confirmation code is: {}'.format(
            username,
            confirmation_code),
        'from@example.com',
        [email],
        fail_silently=False,
    )


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
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer_1.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserGetToken(APIView):
    def post(self, request):
        serializer = UserGetTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = request.data['username']
            confirmation_code = request.data['confirmation_code']

            user = get_object_or_404(User, username=username)
            if default_token_generator.check_token(user, confirmation_code):
                return Response(data={"token": str(AccessToken.for_user(user))})
            return Response(
                data={"confirmation_code": "Некорректный код подтверждения."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminPermission,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path='me',
        permission_classes=[IsUserAuthenticatedPermission]
    )
    def get_me(self, request):

        if request.method == 'GET':
            serializer = MeSerializer(request.user)
            if serializer.is_valid:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance = User.objects.get(username=request.user)
            serializer = MeSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                self.perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)

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
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(
    ListCreateDestroyViewSet
):
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(_rating=Avg("reviews__score")).all()
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
