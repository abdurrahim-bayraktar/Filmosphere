from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

<<<<<<< HEAD
# filmeden gelen ozellikler kalsın save
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
    # basic bunlar
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", login_view, name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # profil islemler icin
    path("profile/me/", current_user_view, name="current-user"),
    path("profile/<str:username>/", UserProfileView.as_view(), name="user-profile"),

    # biraz modification var daha düzenli olması için profiel aldım
    path("profile/<str:username>/ratings/", UserRatingsListView.as_view(), name="user-ratings"),
    path("profile/<str:username>/lists/", UserListsView.as_view(), name="user-lists"),
    path("profile/<str:username>/reviews/", UserReviewsView.as_view(), name="user-reviews"),
    
    # burda sosyal ozelikler var pathi yoktu
    path("profile/<str:username>/badges/", UserBadgesView.as_view(), name="user-badges"),
    path("profile/<str:username>/followers/", UserFollowersView.as_view(), name="user-followers"),
    path("profile/<str:username>/following/", UserFollowingView.as_view(), name="user-following"),
]
=======
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

>>>>>>> feature/backend-api
