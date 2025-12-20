<<<<<<< HEAD
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with additional information."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture_url = models.URLField(max_length=2000, blank=True, null=True)
    favorite_film_1 = models.ForeignKey(
        "films.Film",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="favorite_for_users_1",
    )
    favorite_film_2 = models.ForeignKey(
        "films.Film",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="favorite_for_users_2",
    )
    favorite_film_3 = models.ForeignKey(
        "films.Film",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="favorite_for_users_3",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_userprofile"

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def films_watched_count(self):
        """Count of films the user has watched."""
        try:
            from films.models import WatchedFilm
            return WatchedFilm.objects.filter(user=self.user).count()
        except ImportError:
            return 0

    @property
    def reviews_count(self):
        """Count of reviews written by user."""
        # Will be implemented when Review model is created
        try:
            from films.models import Review
            return Review.objects.filter(user=self.user).count()
        except ImportError:
            return 0

    @property
    def lists_count(self):
        """Count of lists created by user."""
        # Will be implemented when List model is created
        try:
            from films.models import List
            return List.objects.filter(user=self.user).count()
        except ImportError:
            return 0


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile automatically when user is created."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved."""
    if hasattr(instance, "profile"):
        instance.profile.save()


class Follow(models.Model):
    """User following relationship - simple follower system."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        help_text="User who is following",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        help_text="User being followed",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["follower", "following"]]
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

    def clean(self):
        """Prevent users from following themselves."""
        from django.core.exceptions import ValidationError
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves.")

    def save(self, *args, **kwargs):
        """Override save to call clean."""
        self.clean()
        super().save(*args, **kwargs)
=======
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model extending Django's default AbstractUser.
    Additional fields can be added later if needed.
    """
    pass


class Badge(models.Model):
    """
    Achievement badges earned by users based on activity.
    Example: '100 Films Watched', 'Top Commenter', etc.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)  # Internal identifier
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=255, blank=True)  # Icon URL or file path

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    """
    Extended profile information associated with a User.
    Stores avatar, bio, badges, and top favorite movies.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.URLField(blank=True)
    bio = models.TextField(blank=True)

    # Temporary fields for Top 3 favorite movies (linked later to Film model)
    favorite_movie_1 = models.CharField(max_length=255, blank=True)
    favorite_movie_2 = models.CharField(max_length=255, blank=True)
    favorite_movie_3 = models.CharField(max_length=255, blank=True)

    badges = models.ManyToManyField(Badge, blank=True, related_name="profiles")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile({self.user.username})"
    
    

class PasswordResetCode(models.Model):
    """
    Stores temporary reset codes for password recovery.
    Each code is valid only once and for a limited time.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_codes")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"ResetCode({self.user.username}, {self.code})"
>>>>>>> feature/backend-api

