from __future__ import annotations

from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from films.models import (
    Badge, CommentFlag, List, ListItem, Mood, Rating,
    Review, ReviewLike, UserBadge, WatchedFilm
)
from films.models import Follow as FollowRelationship



# ------------------------------
# IMDb Search Result Serializer
# ------------------------------
class SearchResultSerializer(serializers.Serializer):
    imdb_id = serializers.CharField()
    title = serializers.CharField()
    year = serializers.IntegerField(required=False, allow_null=True)
    image = serializers.CharField(required=False, allow_null=True)
    type = serializers.CharField(required=False, allow_null=True)


# ------------------------------
# Rating Serializers
# ------------------------------
class RatingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    film_title = serializers.CharField(source="film.title", read_only=True)
    film_imdb_id = serializers.CharField(source="film.imdb_id", read_only=True)

    class Meta:
        model = Rating
        fields = [
            "id",
            "user",
            "username",
            "film",
            "film_title",
            "film_imdb_id",
            "overall_rating",
            "plot_rating",
            "acting_rating",
            "cinematography_rating",
            "soundtrack_rating",
            "originality_rating",
            "direction_rating",
            "rated_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "rated_at", "updated_at"]

    def validate(self, attrs):
        overall = attrs.get("overall_rating")
        aspects = [
            attrs.get("plot_rating"),
            attrs.get("acting_rating"),
            attrs.get("cinematography_rating"),
            attrs.get("soundtrack_rating"),
            attrs.get("originality_rating"),
            attrs.get("direction_rating"),
        ]
        if not overall and not any(a is not None for a in aspects):
            raise serializers.ValidationError(
                "Either overall_rating or at least one aspect rating must be provided."
            )
        return attrs


class RatingCreateUpdateSerializer(serializers.ModelSerializer):
    overall_rating = serializers.IntegerField(
        required=False,
        allow_null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    class Meta:
        model = Rating
        fields = [
            "overall_rating",
            "plot_rating",
            "acting_rating",
            "cinematography_rating",
            "soundtrack_rating",
            "originality_rating",
            "direction_rating",
        ]

    def validate(self, attrs):
        overall = attrs.get("overall_rating")
        aspects = [
            attrs.get("plot_rating"),
            attrs.get("acting_rating"),
            attrs.get("cinematography_rating"),
            attrs.get("soundtrack_rating"),
            attrs.get("originality_rating"),
            attrs.get("direction_rating"),
        ]
        if not overall and not any(a is not None for a in aspects):
            raise serializers.ValidationError(
                "Either overall_rating or at least one aspect rating must be provided."
            )
        return attrs


# ------------------------------
# Mood Serializers
# ------------------------------
class MoodSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    film_title = serializers.CharField(source="film.title", read_only=True)
    film_imdb_id = serializers.CharField(source="film.imdb_id", read_only=True)

    class Meta:
        model = Mood
        fields = [
            "id",
            "user",
            "username",
            "film",
            "film_title",
            "film_imdb_id",
            "mood_before",
            "mood_after",
            "logged_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "logged_at", "updated_at"]


class MoodCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ["mood_before", "mood_after"]

    def validate_mood_before(self, value):
        if not value:
            raise serializers.ValidationError("mood_before is required.")
        return value


# ------------------------------
# Recommendation Serializer
# ------------------------------
class RecommendationSerializer(serializers.Serializer):
    film_title = serializers.CharField()
    imdb_id = serializers.CharField(required=False, allow_null=True)
    search_url = serializers.CharField(required=False, allow_null=True)
    film_detail_url = serializers.CharField(required=False, allow_null=True)


# ------------------------------
# List & ListItem Serializers (VERSİYON A – chosen)
# ------------------------------
class ListItemSerializer(serializers.ModelSerializer):
    film_title = serializers.CharField(source="film.title", read_only=True)
    film_imdb_id = serializers.CharField(source="film.imdb_id", read_only=True)
    film_poster_url = serializers.URLField(source="film.poster_url", read_only=True)
    film_year = serializers.IntegerField(source="film.year", read_only=True)

    class Meta:
        model = ListItem
        fields = [
            "id",
            "film",
            "film_title",
            "film_imdb_id",
            "film_poster_url",
            "film_year",
            "order",
            "added_at",
        ]
        read_only_fields = ["id", "added_at"]


class ListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    films_count = serializers.IntegerField(read_only=True)
    items = ListItemSerializer(many=True, read_only=True)

    class Meta:
        model = List
        fields = [
            "id",
            "user",
            "username",
            "title",
            "description",
            "is_public",
            "films_count",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at", "films_count"]


class ListCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ["title", "description", "is_public"]


# ------------------------------
# Review Serializers
# ------------------------------
class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    film_title = serializers.CharField(source="film.title", read_only=True)
    film_imdb_id = serializers.CharField(source="film.imdb_id", read_only=True)
    is_liked = serializers.SerializerMethodField()
    contains_spoiler = serializers.BooleanField(read_only=True)
    content = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "username",
            "film",
            "film_title",
            "film_imdb_id",
            "title",
            "content",
            "rating",
            "likes_count",
            "is_liked",
            "is_spoiler",
            "is_auto_detected_spoiler",
            "contains_spoiler",
            "moderation_status",
            "flagged_count",
            "moderation_reason",
            "moderated_at",
            "moderated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "likes_count",
            "is_auto_detected_spoiler",
            "contains_spoiler",
            "moderation_status",
            "flagged_count",
            "moderation_reason",
            "moderated_at",
            "moderated_by",
            "created_at",
            "updated_at",
        ]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return ReviewLike.objects.filter(user=request.user, review=obj).exists()
        return False

    def get_content(self, obj):
        request = self.context.get("request")
        show_spoiler = (
            request and request.query_params.get("show_spoiler", "false").lower() == "true"
        )
        if obj.contains_spoiler and not show_spoiler:
            return "[SPOILER - Click to reveal]"
        return obj.content


class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["title", "content", "rating", "is_spoiler"]

    def validate_rating(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


# ------------------------------
# Follow Serializer
# ------------------------------
class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source="follower.username", read_only=True)
    following_username = serializers.CharField(source="following.username", read_only=True)

    class Meta:
        model = FollowRelationship
        fields = [
            "id",
            "follower",
            "follower_username",
            "following",
            "following_username",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]



# ------------------------------
# Badge + UserBadge Serializers
# ------------------------------
class BadgeSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Badge
        fields = [
            "id",
            "name",
            "description",
            "criteria_type",
            "criteria_value",
            "icon_url",
            "is_custom",
            "created_by",
            "created_by_username",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserBadgeSerializer(serializers.ModelSerializer):
    badge_details = BadgeSerializer(source="badge", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserBadge
        fields = [
            "id",
            "user",
            "username",
            "badge",
            "badge_details",
            "earned_at",
            "progress",
        ]
        read_only_fields = ["id", "earned_at"]


# ------------------------------
# Watched Film Serializer
# ------------------------------
class WatchedFilmSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    film_title = serializers.CharField(source="film.title", read_only=True)
    film_imdb_id = serializers.CharField(source="film.imdb_id", read_only=True)
    film_year = serializers.IntegerField(source="film.year", read_only=True)
    film_poster_url = serializers.URLField(source="film.poster_url", read_only=True)

    class Meta:
        model = WatchedFilm
        fields = [
            "id",
            "user",
            "username",
            "film",
            "film_title",
            "film_imdb_id",
            "film_year",
            "film_poster_url",
            "watched_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "watched_at", "updated_at"]
