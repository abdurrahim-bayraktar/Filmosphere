<<<<<<< HEAD
from django.contrib.auth.models import User
from rest_framework import serializers

from users.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer with stats."""

    user = UserSerializer(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    films_watched_count = serializers.IntegerField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    lists_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "username",
            "email",
            "display_name",
            "bio",
            "profile_picture_url",
            "favorite_film_1",
            "favorite_film_2",
            "favorite_film_3",
            "films_watched_count",
            "reviews_count",
            "lists_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm", "display_name"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        display_name = validated_data.pop("display_name", None)
        password = validated_data.pop("password")

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Set display name if provided
        if display_name:
            user.profile.display_name = display_name
            user.profile.save()

        return user

=======
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile, Badge
from films.models import Follow as FollowRelationship


User = get_user_model()


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["id", "name", "code", "description", "icon"]


class ProfileSerializer(serializers.ModelSerializer):
    badges = BadgeSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            "avatar",
            "bio",
            "favorite_movie_1",
            "favorite_movie_2",
            "favorite_movie_3",
            "badges",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    followers_count = serializers.IntegerField(source="followers.count", read_only=True)
    following_count = serializers.IntegerField(source="following.count", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile", "followers_count", "following_count"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.SlugRelatedField(slug_field="username", read_only=True)
    following = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = FollowRelationship
        fields = ["id", "follower", "following", "created_at"]


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)


# ------------------------------------------------
# NEW: Custom Login Serializer (JWT + User Info)
# ------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends JWT login response with full user info.
    Returned format:
    {
        "refresh": "...",
        "access": "...",
        "user": { id, username, email }
    }
    """

    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
        }

        return data
>>>>>>> feature/backend-api
