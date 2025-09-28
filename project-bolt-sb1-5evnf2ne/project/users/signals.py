from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Artist, Administrator


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == CustomUser.ARTIST:
            Artist.objects.create(
                user=instance,
                full_name=instance.username
            )
        elif instance.user_type == CustomUser.ADMIN:
            Administrator.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == CustomUser.ARTIST:
        if hasattr(instance, 'artist_profile'):
            instance.artist_profile.save()
        else:
            Artist.objects.create(
                user=instance,
                full_name=instance.username
            )
    elif instance.user_type == CustomUser.ADMIN:
        if hasattr(instance, 'admin_profile'):
            instance.admin_profile.save()
        else:
            Administrator.objects.create(user=instance)