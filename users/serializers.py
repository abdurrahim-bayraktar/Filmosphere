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
