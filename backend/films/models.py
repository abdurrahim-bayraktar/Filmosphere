import uuid
from decimal import Decimal


from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Count


class Film(models.Model):
    """Persistent cache of aggregated film data keyed by IMDb id."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    imdb_id = models.CharField(max_length=20, unique=True, db_index=True)
    title = models.CharField(max_length=512, db_index=True)
    year = models.IntegerField(null=True, blank=True)
    poster_url = models.URLField(max_length=2000, null=True, blank=True)
    full_json = models.JSONField(null=True, blank=True)
    cached_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["imdb_id"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.imdb_id})"

    def get_average_ratings(self):
        """Calculate average ratings for all aspects from all user ratings."""
        ratings = Rating.objects.filter(film=self)

        if not ratings.exists():
            return {
                "overall": None,
                "plot": None,
                "acting": None,
                "cinematography": None,
                "soundtrack": None,
                "originality": None,
                "direction": None,
                "total_ratings": 0,
            }

        aspect_ratings = ratings.aggregate(
            avg_overall=Avg("overall_rating"),
            avg_plot=Avg("plot_rating"),
            avg_acting=Avg("acting_rating"),
            avg_cinematography=Avg("cinematography_rating"),
            avg_soundtrack=Avg("soundtrack_rating"),
            avg_originality=Avg("originality_rating"),
            avg_direction=Avg("direction_rating"),
            total=Count("id"),
        )

        return {
            "overall": round(float(aspect_ratings["avg_overall"] or 0), 2),
            "plot": round(float(aspect_ratings["avg_plot"] or 0), 2) if aspect_ratings["avg_plot"] else None,
            "acting": round(float(aspect_ratings["avg_acting"] or 0), 2) if aspect_ratings["avg_acting"] else None,
            "cinematography": round(float(aspect_ratings["avg_cinematography"] or 0), 2) if aspect_ratings["avg_cinematography"] else None,
            "soundtrack": round(float(aspect_ratings["avg_soundtrack"] or 0), 2) if aspect_ratings["avg_soundtrack"] else None,
            "originality": round(float(aspect_ratings["avg_originality"] or 0), 2) if aspect_ratings["avg_originality"] else None,
            "direction": round(float(aspect_ratings["avg_direction"] or 0), 2) if aspect_ratings["avg_direction"] else None,
            "total_ratings": aspect_ratings["total"],
        }


class Rating(models.Model):
    """Advanced multi-aspect rating system for films."""

    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # 1-5 scale

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="ratings")

    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall rating (1-5). If aspect ratings provided, this is calculated automatically.",
    )

    plot_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Plot rating (1-5)",
    )
    acting_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Acting rating (1-5)",
    )
    cinematography_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Cinematography rating (1-5)",
    )
    soundtrack_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Soundtrack rating (1-5)",
    )
    originality_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Originality rating (1-5)",
    )
    direction_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Direction rating (1-5)",
    )

    rated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["user", "film"]]
        indexes = [
            models.Index(fields=["user", "film"]),
            models.Index(fields=["film"]),
        ]
        ordering = ["-rated_at"]

    def __str__(self):
        return f"{self.user.username} rated {self.film.title} {self.overall_rating}/5"

    def calculate_overall_from_aspects(self):
        aspects = [
            self.plot_rating,
            self.acting_rating,
            self.cinematography_rating,
            self.soundtrack_rating,
            self.originality_rating,
            self.direction_rating,
        ]
        provided = [a for a in aspects if a is not None]
        return round(sum(provided) / len(provided)) if provided else None

    def has_aspect_ratings(self):
        return any([
            self.plot_rating, self.acting_rating,
            self.cinematography_rating, self.soundtrack_rating,
            self.originality_rating, self.direction_rating,
        ])

    def save(self, *args, **kwargs):
        if self.has_aspect_ratings():
            calculated = self.calculate_overall_from_aspects()
            if calculated:
                self.overall_rating = calculated
        super().save(*args, **kwargs)


class List(models.Model):
    """Custom film lists created by users (FR03)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lists")
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    is_public = models.BooleanField(default=True, help_text="Whether the list is visible to other users")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_public"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}'s List: {self.title}"

    @property
    def films_count(self):
        return self.items.count()


class ListItem(models.Model):
    """Individual film in a list (FR03.2, FR03.3)."""

    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="items")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="list_items")
    order = models.IntegerField(default=0, help_text="Position in the list")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["list", "film"]]
        indexes = [
            models.Index(fields=["list", "order"]),
        ]
        ordering = ["order", "added_at"]

    def __str__(self):
        return f"{self.film.title} in {self.list.title}"


class Review(models.Model):
    """User reviews/comments for films."""

    MODERATION_STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="reviews")

    title = models.CharField(max_length=200)
    content = models.TextField()

    rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Optional rating (1-5) associated with the review",
    )

    likes_count = models.IntegerField(default=0)

    is_spoiler = models.BooleanField(
        default=False,
        help_text="Whether the user manually marked this as a spoiler (FR06.1)",
    )
    is_auto_detected_spoiler = models.BooleanField(
        default=False,
        help_text="Whether the system automatically detected this as a spoiler (FR06.2)",
    )

    moderation_status = models.CharField(
        max_length=20,
        choices=MODERATION_STATUS_CHOICES,
        default="pending",
        help_text="Moderation status: pending, approved, or rejected",
    )
    flagged_count = models.IntegerField(
        default=0,
        help_text="Number of times this comment has been flagged by users",
    )
    moderation_reason = models.TextField(
        blank=True, null=True,
        help_text="Reason for moderation decision (e.g., blacklisted words detected)",
    )
    moderated_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When this comment was moderated by admin",
    )
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="moderated_reviews",
        help_text="Admin user who moderated this comment",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["film", "created_at"]),
            models.Index(fields=["user"]),
            models.Index(fields=["moderation_status"]),
            models.Index(fields=["flagged_count"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}'s review of {self.film.title} ({self.moderation_status})"


class ReviewLike(models.Model):
    """Users liking reviews."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_likes")
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "review"]]
        indexes = [
            models.Index(fields=["review"]),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.review.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.review.likes_count = self.review.likes.count()
        self.review.save(update_fields=["likes_count"])

    def delete(self, *args, **kwargs):
        review = self.review
        super().delete(*args, **kwargs)
        review.likes_count = review.likes.count()
        review.save(update_fields=["likes_count"])


class CommentFlag(models.Model):
    """Users flagging comments for review."""

    FLAG_REASON_CHOICES = [
        ("spam", "Spam"),
        ("inappropriate", "Inappropriate Content"),
        ("harassment", "Harassment"),
        ("hate_speech", "Hate Speech"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_flags")
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="flags")

    reason = models.CharField(
        max_length=20,
        choices=FLAG_REASON_CHOICES,
        default="other",
        help_text="Reason for flagging the comment",
    )
    description = models.TextField(
        blank=True, null=True, max_length=500,
        help_text="Additional details about why this comment was flagged",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "review"]]
        indexes = [
            models.Index(fields=["review"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} flagged {self.review.title} ({self.reason})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.review.flagged_count = self.review.flags.count()
        self.review.save(update_fields=["flagged_count"])

    def delete(self, *args, **kwargs):
        review = self.review
        super().delete(*args, **kwargs)
        review.flagged_count = review.flags.count()
        review.save(update_fields=["flagged_count"])


class Mood(models.Model):
    """Track user's emotional state before and after watching a film (FR09)."""

    MOOD_CHOICES = [
        ("happy", "Happy"),
        ("sad", "Sad"),
        ("excited", "Excited"),
        ("calm", "Calm"),
        ("anxious", "Anxious"),
        ("bored", "Bored"),
        ("energetic", "Energetic"),
        ("relaxed", "Relaxed"),
        ("stressed", "Stressed"),
        ("neutral", "Neutral"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="moods")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="moods")

    mood_before = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES,
        help_text="Emotional state before watching the film",
    )
    mood_after = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES,
        null=True, blank=True,
        help_text="Emotional state after watching the film",
    )

    logged_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["user", "film"]]
        indexes = [
            models.Index(fields=["user", "film"]),
            models.Index(fields=["film"]),
        ]
        ordering = ["-logged_at"]

    def __str__(self):
        return f"{self.user.username}'s mood for {self.film.title}: {self.mood_before} → {self.mood_after or 'N/A'}"


class Badge(models.Model):
    """Badge definitions for the badge system (FR05)."""

    BADGE_TYPES = [
        ("films_watched", "Films Watched"),
        ("reviews_written", "Reviews Written"),
        ("lists_created", "Lists Created"),
        ("ratings_given", "Ratings Given"),
        ("followers_count", "Followers Count"),
        ("custom", "Custom Challenge"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)

    criteria_type = models.CharField(
        max_length=50,
        choices=BADGE_TYPES,
        help_text="Type of criteria for earning this badge (FR05.1)",
    )
    criteria_value = models.IntegerField(
        help_text="Value needed to earn this badge (e.g., 10 films watched)",
    )

    icon_url = models.URLField(
        max_length=2000, blank=True, null=True,
        help_text="URL to badge icon/image",
    )
    is_custom = models.BooleanField(
        default=False,
        help_text="Whether this is a user-created custom badge",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_badges",
        help_text="User who created this badge (for custom badges)",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["criteria_type"]),
            models.Index(fields=["is_custom"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.criteria_type}: {self.criteria_value})"


class UserBadge(models.Model):
    """Badges earned by users (FR05.2, FR05.3)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="user_badges")

    earned_at = models.DateTimeField(auto_now_add=True)

    progress = models.IntegerField(
        default=0,
        help_text="Current progress towards badge (for tracking)",
    )

    class Meta:
        unique_together = [["user", "badge"]]
        indexes = [
            models.Index(fields=["user", "earned_at"]),
            models.Index(fields=["badge"]),
        ]
        ordering = ["-earned_at"]

    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"


class WatchedFilm(models.Model):
    """Track films that users have watched."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watched_films")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="watched_by_users")

    watched_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the user marked the film as watched",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["user", "film"]]
        indexes = [
            models.Index(fields=["user", "watched_at"]),
            models.Index(fields=["film"]),
        ]
        ordering = ["-watched_at"]

    def __str__(self):
        return f"{self.user.username} watched {self.film.title}"
    

class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["follower", "following"]]

    def __str__(self):
        return f"{self.follower} → {self.following}"

