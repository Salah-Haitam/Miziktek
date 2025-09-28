from django.db import models
from django.conf import settings
from mutagen.mp3 import MP3
import os
from datetime import timedelta
from django.db.models import Avg, Sum
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Music(models.Model):
    GENRE_CHOICES = [
        ('pop', 'Pop'),
        ('rock', 'Rock'),
        ('jazz', 'Jazz'),
        ('classical', 'Classical'),
        ('hip_hop', 'Hip Hop'),
        ('electronic', 'Electronic'),
        ('country', 'Country'),
        ('r_and_b', 'R&B'),
        ('indie', 'Indie'),
        ('chaabi','chaabi'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=100)
    artist = models.ForeignKey('users.Artist', on_delete=models.CASCADE, related_name='music')
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='other')
    duration = models.DurationField(null=True, blank=True)
    release_date = models.DateField()
    audio_file = models.FileField(upload_to='music/')
    cover_image = models.ImageField(upload_to='covers/', default='covers/default.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Music'
        ordering = ['-release_date']
    
    def __str__(self):
        return f"{self.title} - {self.artist.full_name}"
    
    def save(self, *args, **kwargs):
        # Calculate duration if not provided
        if not self.duration and self.audio_file:
            try:
                # Save first to have access to the file path
                super().save(*args, **kwargs)
                file_path = self.audio_file.path
                audio = MP3(file_path)
                # Convert seconds to duration
                self.duration = timedelta(seconds=int(audio.info.length))
                # Save again with the duration
                super().save(*args, **kwargs)
            except Exception as e:
                print(f"Error calculating duration: {e}")
        else:
            super().save(*args, **kwargs)

    def get_statistics(self):
        try:
            return self.statistics
        except MusicStatistics.DoesNotExist:
            return MusicStatistics.objects.create(music=self)


class ListeningHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    listened_at = models.DateTimeField(auto_now_add=True)
    listened_duration = models.DurationField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Listening Histories'
        ordering = ['-listened_at']

    def __str__(self):
        return f"{self.user.username} listened to {self.music.title}"


class UserMusicPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)
    favorite = models.BooleanField(default=False)
    last_listened = models.DateTimeField(auto_now=True)
    listen_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'music']

    def __str__(self):
        return f"{self.user.username}'s preference for {self.music.title}"

    @classmethod
    def get_user_preferred_genres(cls, user, limit=3):
        return cls.objects.filter(
            user=user,
            rating__isnull=False
        ).values('music__genre').annotate(
            avg_rating=Avg('rating')
        ).order_by('-avg_rating')[:limit]

    @classmethod
    def get_user_preferred_artists(cls, user, limit=3):
        return cls.objects.filter(
            user=user,
            rating__isnull=False
        ).values('music__artist').annotate(
            avg_rating=Avg('rating')
        ).order_by('-avg_rating')[:limit]


class MusicStatistics(models.Model):
    music = models.OneToOneField(Music, on_delete=models.CASCADE, related_name='statistics')
    total_plays = models.PositiveIntegerField(default=0)
    unique_listeners = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    total_favorites = models.PositiveIntegerField(default=0)
    last_played = models.DateTimeField(null=True, blank=True)
    total_duration_played = models.DurationField(default=timedelta())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Music Statistics'

    def __str__(self):
        return f"Statistics for {self.music.title}"

    def update_statistics(self):
        # Update total plays and unique listeners
        history = ListeningHistory.objects.filter(music=self.music)
        self.total_plays = history.count()
        self.unique_listeners = history.values('user').distinct().count()

        # Update total duration played
        total_duration = history.aggregate(total=Sum('listened_duration'))['total']
        self.total_duration_played = total_duration if total_duration else timedelta()

        # Update average rating
        ratings = UserMusicPreference.objects.filter(music=self.music, rating__isnull=False)
        avg_rating = ratings.aggregate(avg=Avg('rating'))['avg']
        self.average_rating = round(avg_rating, 2) if avg_rating else 0.0

        # Update total favorites
        self.total_favorites = UserMusicPreference.objects.filter(music=self.music, favorite=True).count()

        # Update last played
        last_play = history.order_by('-listened_at').first()
        self.last_played = last_play.listened_at if last_play else None

        self.save()


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    music = models.ManyToManyField(Music, related_name='playlists')
    total_duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Appeler la méthode parente
        super().save(*args, **kwargs)
        # Mettre à jour la durée totale uniquement si ce n'est pas une mise à jour de la durée
        if 'update_fields' not in kwargs or 'total_duration' not in kwargs.get('update_fields', []):
            self.update_duration()

    def update_duration(self):
        # Calculer la nouvelle durée totale
        total = timedelta()
        for music in self.music.all():
            if music.duration:
                total += music.duration
        
        # Ne sauvegarder que si la durée a changé
        if self.total_duration != total:
            self.total_duration = total
            self.save(update_fields=['total_duration'])


@receiver(post_save, sender=ListeningHistory)
def update_statistics_on_history(sender, instance, created, **kwargs):
    if created:
        instance.music.get_statistics().update_statistics()


@receiver(post_save, sender=UserMusicPreference)
def update_statistics_on_preference(sender, instance, **kwargs):
    instance.music.statistics.update_statistics()


@receiver(post_save, sender=Music)
def create_music_statistics(sender, instance, created, **kwargs):
    if created:
        MusicStatistics.objects.create(music=instance)
