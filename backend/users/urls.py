from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    CurrentUserView,
    CustomLoginView,
    FollowToggleView,
    UserFollowersView,
    UserFollowingView,
    ForgotPasswordView,
    ResetPasswordView,
    UpdateProfileView,
)


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", CustomLoginView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),


    path("auth/profile/update/", UpdateProfileView.as_view(), name="profile-update"),

    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),

    path("users/<str:username>/follow-toggle/", FollowToggleView.as_view(), name="follow-toggle"),
    path("users/<str:username>/followers/", UserFollowersView.as_view(), name="user-followers"),
    path("users/<str:username>/following/", UserFollowingView.as_view(), name="user-following"),
]

