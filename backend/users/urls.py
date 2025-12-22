from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

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
    # basic bunlar - Frontend /api/auth/register/ bekliyor
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", login_view, name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # profil islemler icin
    path("auth/me/", current_user_view, name="current-user"),
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
