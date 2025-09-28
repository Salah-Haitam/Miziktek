from django.contrib import admin
from .models import Music, Playlist

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'duration', 'release_date')
    list_filter = ('genre', 'release_date')
    search_fields = ('title', 'artist__full_name')
    date_hierarchy = 'release_date'


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'total_duration', 'created_at')
    filter_horizontal = ('music',)