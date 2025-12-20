from django.contrib import admin

from films.models import Badge, CommentFlag, Film, List, ListItem, Mood, Rating, Review, ReviewLike, UserBadge, WatchedFilm


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ["title", "imdb_id", "year", "created_at"]
    search_fields = ["title", "imdb_id"]
    list_filter = ["year", "created_at"]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "film",
        "overall_rating",
        "plot_rating",
        "acting_rating",
        "cinematography_rating",
        "soundtrack_rating",
        "originality_rating",
        "direction_rating",
        "rated_at",
    ]
    list_filter = ["rated_at", "overall_rating"]
    search_fields = ["user__username", "film__title", "film__imdb_id"]
    readonly_fields = ["rated_at", "updated_at"]
    raw_id_fields = ["user", "film"]


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "film",
        "mood_before",
        "mood_after",
        "logged_at",
    ]
    list_filter = ["logged_at", "mood_before", "mood_after"]
    search_fields = ["user__username", "film__title", "film__imdb_id"]
    readonly_fields = ["logged_at", "updated_at"]
    raw_id_fields = ["user", "film"]


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "is_public", "films_count", "created_at"]
    list_filter = ["is_public", "created_at"]
    search_fields = ["title", "user__username"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["user"]


@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ["list", "film", "order", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["list__title", "film__title"]
    raw_id_fields = ["list", "film"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "user",
        "film",
        "rating",
        "moderation_status",
        "flagged_count",
        "likes_count",
        "created_at",
    ]
    list_filter = ["created_at", "rating", "moderation_status", "flagged_count"]
    search_fields = ["title", "user__username", "film__title", "content"]
    readonly_fields = ["created_at", "updated_at", "likes_count", "flagged_count", "moderated_at"]
    raw_id_fields = ["user", "film", "moderated_by"]
    
    def get_queryset(self, request):
        """Show flagged/pending comments first for admin."""
        qs = super().get_queryset(request)
        return qs.select_related("user", "film", "moderated_by")
    
    actions = ["approve_comments", "reject_comments"]
    
    def approve_comments(self, request, queryset):
        """Approve selected comments."""
        from django.utils import timezone
        updated = queryset.update(
            moderation_status="approved",
            moderated_by=request.user,
            moderated_at=timezone.now(),
        )
        self.message_user(request, f"{updated} comments approved.")
    approve_comments.short_description = "Approve selected comments"
    
    def reject_comments(self, request, queryset):
        """Reject selected comments."""
        from django.utils import timezone
        updated = queryset.update(
            moderation_status="rejected",
            moderated_by=request.user,
            moderated_at=timezone.now(),
        )
        self.message_user(request, f"{updated} comments rejected.")
    reject_comments.short_description = "Reject selected comments"


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "review", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "review__title"]
    raw_id_fields = ["user", "review"]


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ["name", "criteria_type", "criteria_value", "is_custom", "created_by", "created_at"]
    list_filter = ["criteria_type", "is_custom", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["created_by"]


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ["user", "badge", "earned_at", "progress"]
    list_filter = ["earned_at", "badge"]
    search_fields = ["user__username", "badge__name"]
    readonly_fields = ["earned_at"]
    raw_id_fields = ["user", "badge"]


@admin.register(WatchedFilm)
class WatchedFilmAdmin(admin.ModelAdmin):
    list_display = ["user", "film", "watched_at"]
    list_filter = ["watched_at"]
    search_fields = ["user__username", "film__title", "film__imdb_id"]
    readonly_fields = ["watched_at", "updated_at"]
    raw_id_fields = ["user", "film"]


@admin.register(CommentFlag)
class CommentFlagAdmin(admin.ModelAdmin):
    list_display = ["review", "user", "reason", "created_at"]
    list_filter = ["reason", "created_at"]
    search_fields = ["review__title", "user__username", "description"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["user", "review"]

