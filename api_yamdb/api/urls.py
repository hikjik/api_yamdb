from api.views import CategoryViewSet, GenreViewSet, TitleViewSet, UserSignUp, UserGetToken, UsersViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

v1_router = DefaultRouter()
v1_router.register('categories', CategoryViewSet)
v1_router.register('genres', GenreViewSet)
v1_router.register('titles', TitleViewSet)
v1_router.register('users', UsersViewSet)



urlpatterns = [
    path('v1/auth/signup/', UserSignUp.as_view()),
    path('v1/auth/token/', UserGetToken.as_view()),
    path('v1/', include(v1_router.urls)),
]
