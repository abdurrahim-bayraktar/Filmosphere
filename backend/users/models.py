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

