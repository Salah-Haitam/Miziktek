from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    REGULAR_USER = 'regular'
    ARTIST = 'artist'
    ADMIN = 'admin'
    
    USER_TYPE_CHOICES = [
        (REGULAR_USER, 'Regular User'),
        (ARTIST, 'Artist'),
        (ADMIN, 'Administrator'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default=REGULAR_USER
    )
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        default='profile_images/default.png'
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def is_artist(self):
        return self.user_type == self.ARTIST
    
    def is_admin(self):
        return self.user_type == self.ADMIN
    
    def is_regular_user(self):
        return self.user_type == self.REGULAR_USER


class Artist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='artist_profile'
    )
    full_name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='artist_images/', null=True, blank=True)
    
    def __str__(self):
        return self.full_name


class Administrator(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_profile'
    )
    
    def __str__(self):
        return self.user.username