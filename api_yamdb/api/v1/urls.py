from rest_framework.routers import DefaultRouter

from .views import (AuthViewSet, CategoryViewSet, CommentViewSet,
                    GenreViewSet, ReviewViewSet, TitleViewSet,
                    UserViewSet)

v1_router = DefaultRouter()
v1_router.register("auth", AuthViewSet)
v1_router.register("users", UserViewSet)
v1_router.register("categories", CategoryViewSet)
v1_router.register("genres", GenreViewSet)
v1_router.register("titles", TitleViewSet)
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews",
    ReviewViewSet,
    basename="reviews",
)
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)

urlpatterns = v1_router.urls
