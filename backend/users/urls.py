from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from films.views import (
    UserBadgesView,
    UserFollowersView,
    UserFollowingView,
    UserListsView,
    UserRatingsListView,
    UserReviewsView,
)
from users.views import (
    RegisterView,
    login_view,
    UserProfileView,
    current_user_view,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", login_view, name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/", current_user_view, name="current-user"),
    path("users/<str:username>/", UserProfileView.as_view(), name="user-profile"),
    path("users/<str:username>/ratings/", UserRatingsListView.as_view(), name="user-ratings"),
    path("users/<str:username>/lists/", UserListsView.as_view(), name="user-lists"),
    path("users/<str:username>/reviews/", UserReviewsView.as_view(), name="user-reviews"),
]

