from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import UserProfile
from users.serializers import (
    UserProfileSerializer,
    UserRegistrationSerializer,
)


class RegisterView(CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint."""
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"detail": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        },
        status=status.HTTP_200_OK,
    )


class UserProfileView(RetrieveUpdateAPIView):
    """Get or update user profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "username"
    lookup_url_kwarg = "username"

    def get_queryset(self):
        return UserProfile.objects.select_related("user").all()

    def get_object(self):
        username = self.kwargs.get("username")
        if username == "me":
            return self.request.user.profile
        return UserProfile.objects.get(user__username=username)

    def update(self, request, *args, **kwargs):
        """Only allow users to update their own profile."""
        username = self.kwargs.get("username")
        if username != "me" and request.user.username != username:
            return Response(
                {"detail": "You can only update your own profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Get current authenticated user's profile."""
    serializer = UserProfileSerializer(request.user.profile)
    return Response(serializer.data)
