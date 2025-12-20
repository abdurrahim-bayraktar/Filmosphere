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
