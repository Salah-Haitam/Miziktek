from .models import UserMusicPreference

def favorite_count(request):
    """Add favorite count to the context."""
    if request.user.is_authenticated:
        count = UserMusicPreference.objects.filter(
            user=request.user,
            favorite=True
        ).count()
        return {'favorite_count': count}
    return {'favorite_count': 0}
