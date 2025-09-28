from django.db.models import Q, Count
from .models import Music, UserMusicPreference, ListeningHistory, Playlist


def get_recommendations(user, limit=10):
    """
    Get personalized music recommendations for a user based on:
    1. Their preferred genres
    2. Their preferred artists
    3. Similar users' preferences
    4. Popular songs in their playlists' genres
    """
    recommendations = []
    
    # Get user's listening history to exclude already listened songs
    listened_music_ids = ListeningHistory.objects.filter(user=user).values_list('music_id', flat=True)
    
    # 1. Get recommendations based on preferred genres
    preferred_genres = UserMusicPreference.get_user_preferred_genres(user)
    genre_recommendations = Music.objects.filter(
        genre__in=[g['music__genre'] for g in preferred_genres]
    ).exclude(
        id__in=listened_music_ids
    )[:limit]
    recommendations.extend(list(genre_recommendations))

    # 2. Get recommendations based on preferred artists
    preferred_artists = UserMusicPreference.get_user_preferred_artists(user)
    artist_recommendations = Music.objects.filter(
        artist__in=[a['music__artist'] for a in preferred_artists]
    ).exclude(
        id__in=listened_music_ids
    ).exclude(
        id__in=[m.id for m in recommendations]
    )[:limit]
    recommendations.extend(list(artist_recommendations))

    # 3. Get recommendations based on similar users
    similar_users = UserMusicPreference.objects.filter(
        music__in=UserMusicPreference.objects.filter(
            user=user, rating__isnull=False
        ).values_list('music', flat=True)
    ).exclude(
        user=user
    ).values_list('user', flat=True).distinct()

    similar_users_recommendations = Music.objects.filter(
        usermusicpreference__user__in=similar_users,
        usermusicpreference__rating__gte=4
    ).exclude(
        id__in=listened_music_ids
    ).exclude(
        id__in=[m.id for m in recommendations]
    ).annotate(
        recommendation_count=Count('id')
    ).order_by('-recommendation_count')[:limit]
    recommendations.extend(list(similar_users_recommendations))

    # 4. Get popular songs from user's playlists' genres
    playlist_genres = Music.objects.filter(
        playlists__creator=user
    ).values_list('genre', flat=True).distinct()

    playlist_recommendations = Music.objects.filter(
        genre__in=playlist_genres
    ).exclude(
        id__in=listened_music_ids
    ).exclude(
        id__in=[m.id for m in recommendations]
    ).annotate(
        playlist_count=Count('playlists')
    ).order_by('-playlist_count')[:limit]
    recommendations.extend(list(playlist_recommendations))

    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = []
    for item in recommendations:
        if item.id not in seen:
            seen.add(item.id)
            unique_recommendations.append(item)

    return unique_recommendations[:limit]


def update_user_preferences(user, music, rating=None, listened_duration=None):
    """
    Update user preferences and listening history when a user interacts with a song
    """
    # Update or create user preference
    preference, created = UserMusicPreference.objects.get_or_create(
        user=user,
        music=music,
        defaults={'listen_count': 1}
    )
    
    if not created:
        preference.listen_count += 1
    
    if rating is not None:
        preference.rating = rating
    
    preference.save()

    # Record listening history
    ListeningHistory.objects.create(
        user=user,
        music=music,
        listened_duration=listened_duration
    )
