from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, Profile


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """
    Automatically create a Profile whenever a new User is created.
    Ensures each user always has an associated Profile object.
    """
    if created:
        Profile.objects.create(user=instance)
