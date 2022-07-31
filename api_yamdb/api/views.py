from api.serializers import (CategorySerializer, GenreSerializer,
                             TitleSerializer, UserSingUpSerializer, 
                             UserGetTokenSerializer, UserSerializer)
from rest_framework import viewsets
from reviews.models import Category, Genre, Title, User
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
import hashlib
from datetime import datetime
from django.core.mail import send_mail
from .permissions import IsAdminPermission


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


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
    user_obj = User.objects.filter(username = username)
    user_obj.update(confirmation_code = confirmation_code)
    return confirmation_code


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
    }


class UserSignUp(APIView):

    def post(self, request):
        serializer = UserSingUpSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            send_confirmation_code(
                request.data['username'],
                request.data['email']
            )
            return Response(serializer.data)
        return Response(serializer.errors)
   

class UserGetToken(APIView):
    def post(self, request):
        serializer = UserGetTokenSerializer(data = request.data)
        if serializer.is_valid():
            jwt_token = get_tokens_for_user(User.objects.get(username = request.data['username']))
            return Response({'JWT token': jwt_token})
        else:
            return Response(serializer.errors)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminPermission,)

    def perform_create(self, serializer):
        serializer.save()
        send_confirmation_code(self.request.data['username'], self.request.data['email'])







    
