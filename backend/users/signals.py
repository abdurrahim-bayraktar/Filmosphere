from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import UserProfile


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile whenever a new User is created.
    Ensures each user always has an associated UserProfile object.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
