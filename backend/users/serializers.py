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
