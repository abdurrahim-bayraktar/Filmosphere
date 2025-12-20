<<<<<<< HEAD
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

=======
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
import random

from rest_framework_simplejwt.views import TokenObtainPairView

# MODELS
from .models import PasswordResetCode
from films.models import Follow as FollowRelationship

# SERIALIZERS
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    FollowSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
)

User = get_user_model()


# -----------------------------
# AUTH SYSTEM
# -----------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# NEW: Custom Login View
class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# -----------------------------
# FOLLOW SYSTEM
# -----------------------------
class FollowToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        if target == request.user:
            return Response({"detail": "You cannot follow yourself."}, status=400)

        relation, created = FollowRelationship.objects.get_or_create(
            follower=request.user,
            following=target,
        )

        if not created:
            relation.delete()
            return Response({"status": "unfollowed"})

        return Response({"status": "followed"})


class UserFollowersView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = User.objects.get(username=self.kwargs["username"])
        return FollowRelationship.objects.filter(following=user)


class UserFollowingView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = User.objects.get(username=self.kwargs["username"])
        return FollowRelationship.objects.filter(follower=user)


# -----------------------------
# FORGOT PASSWORD
# -----------------------------
class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "No account found with this email."}, status=404)

        code = f"{random.randint(100000, 999999)}"
        PasswordResetCode.objects.create(user=user, code=code)

        return Response({
            "message": "Reset code generated.",
            "reset_code": code
        })


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        password = serializer.validated_data["password"]

        try:
            reset_entry = PasswordResetCode.objects.get(code=code, is_used=False)
        except PasswordResetCode.DoesNotExist:
            return Response({"detail": "Invalid or expired reset code."}, status=400)

        user = reset_entry.user
        user.set_password(password)
        user.save()

        reset_entry.is_used = True
        reset_entry.save()

        return Response({"message": "Password reset successful."})


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
>>>>>>> feature/backend-api
