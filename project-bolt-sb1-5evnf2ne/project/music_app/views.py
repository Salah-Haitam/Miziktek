from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from .models import Music, Playlist, UserMusicPreference, ListeningHistory
from .forms import MusicUploadForm, PlaylistForm
from users.models import CustomUser
from django.db.models import Q
from .recommendations import get_recommendations, update_user_preferences


def home(request):
    recent_music = Music.objects.all().order_by('-release_date')[:5]
    
    # Get personalized recommendations for authenticated users
    recommended_music = []
    if request.user.is_authenticated:
        recommended_music = get_recommendations(request.user, limit=5)
    
    # For non-authenticated users, show default playlist
    default_playlist = None
    if not request.user.is_authenticated:
        # Try to get a default playlist, or create one if needed
        try:
            admin_user = CustomUser.objects.filter(user_type=CustomUser.ADMIN).first()
            default_playlist = Playlist.objects.filter(creator=admin_user).first()
        except:
            pass
    
    return render(request, 'music_app/home.html', {
        'recent_music': recent_music,
        'recommended_music': recommended_music,
        'default_playlist': default_playlist
    })


def music_list(request):
    genre_filter = request.GET.get('genre', '')
    search_query = request.GET.get('search', '')
    
    music = Music.objects.all()
    
    if genre_filter:
        music = music.filter(genre=genre_filter)
    
    if search_query:
        music = music.filter(
            Q(title__icontains=search_query) | 
            Q(artist__full_name__icontains=search_query)
        )
    
    return render(request, 'music_app/music_list.html', {
        'music_list': music,
        'genres': dict(Music.GENRE_CHOICES),
        'current_genre': genre_filter,
        'search_query': search_query
    })


def music_detail(request, pk):
    music = get_object_or_404(Music, pk=pk)
    
    # Get playlists containing this music, if user is authenticated
    user_playlists = []
    user_preference = None
    similar_music = []
    
    if request.user.is_authenticated:
        user_playlists = Playlist.objects.filter(
            creator=request.user,
            music=music
        )
        
        # Get or create user preference
        user_preference, _ = UserMusicPreference.objects.get_or_create(
            user=request.user,
            music=music
        )
        
        # Get similar music based on genre and artist
        similar_music = Music.objects.filter(
            Q(genre=music.genre) | Q(artist=music.artist)
        ).exclude(id=music.id)[:5]
        
        # Record listening history
        update_user_preferences(request.user, music)
    
    return render(request, 'music_app/music_detail.html', {
        'music': music,
        'user_playlists': user_playlists,
        'user_preference': user_preference,
        'similar_music': similar_music
    })


@login_required
def upload_music(request):
    # Only artists and admins can upload music
    if not (request.user.is_artist() or request.user.is_admin()):
        return HttpResponseForbidden("You don't have permission to upload music.")
    
    if request.method == 'POST':
        form = MusicUploadForm(request.POST, request.FILES)
        if form.is_valid():
            music = form.save(commit=False)
            
            # Assign the artist
            if request.user.is_artist():
                music.artist = request.user.artist_profile
            elif request.user.is_admin() and 'artist' in request.POST:
                artist_id = request.POST.get('artist')
                music.artist_id = artist_id
            
            music.save()
            messages.success(request, 'Music uploaded successfully!')
            return redirect('music_detail', pk=music.pk)
    else:
        form = MusicUploadForm()
    
    return render(request, 'music_app/music_form.html', {
        'form': form,
        'title': 'Upload Music'
    })


@login_required
def edit_music(request, pk):
    music = get_object_or_404(Music, pk=pk)
    
    # Only the artist who uploaded the music or an admin can edit it
    if not (request.user.is_admin() or 
           (request.user.is_artist() and music.artist.user == request.user)):
        return HttpResponseForbidden("You don't have permission to edit this music.")
    
    if request.method == 'POST':
        form = MusicUploadForm(request.POST, request.FILES, instance=music)
        if form.is_valid():
            form.save()
            messages.success(request, 'Music updated successfully!')
            return redirect('music_detail', pk=music.pk)
    else:
        form = MusicUploadForm(instance=music)
    
    return render(request, 'music_app/music_form.html', {
        'form': form,
        'title': 'Edit Music',
        'music': music
    })


@login_required
def delete_music(request, pk):
    music = get_object_or_404(Music, pk=pk)
    
    # Only the artist who uploaded the music or an admin can delete it
    if not (request.user.is_admin() or 
           (request.user.is_artist() and music.artist.user == request.user)):
        return HttpResponseForbidden("You don't have permission to delete this music.")
    
    if request.method == 'POST':
        music.delete()
        messages.success(request, 'Music deleted successfully!')
        return redirect('music_list')
    
    return render(request, 'music_app/music_confirm_delete.html', {'music': music})


def playlist_list(request):
    if request.user.is_authenticated:
        # Show user's playlists
        playlists = Playlist.objects.filter(creator=request.user)
    else:
        # Show some public playlists for non-authenticated users
        playlists = Playlist.objects.all()[:5]
    
    return render(request, 'music_app/playlist_list.html', {'playlists': playlists})


def playlist_detail(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    return render(request, 'music_app/playlist_detail.html', {'playlist': playlist})


@login_required
def create_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST, user=request.user)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.creator = request.user
            playlist.save()
            # Save the many-to-many relationships
            form.save_m2m()
            # Update the duration
            playlist.update_duration()
            messages.success(request, 'Playlist created successfully!')
            return redirect('playlist_detail', pk=playlist.pk)
    else:
        form = PlaylistForm(user=request.user)
    
    return render(request, 'music_app/playlist_form.html', {
        'form': form,
        'title': 'Create Playlist'
    })


@login_required
def edit_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    
    # Only the creator or an admin can edit the playlist
    if not (request.user.is_admin() or playlist.creator == request.user):
        return HttpResponseForbidden("You don't have permission to edit this playlist.")
    
    if request.method == 'POST':
        form = PlaylistForm(request.POST, instance=playlist, user=request.user)
        if form.is_valid():
            form.save()
            # Update the duration
            playlist.update_duration()
            messages.success(request, 'Playlist updated successfully!')
            return redirect('playlist_detail', pk=playlist.pk)
    else:
        form = PlaylistForm(instance=playlist, user=request.user)
    
    return render(request, 'music_app/playlist_form.html', {
        'form': form,
        'title': 'Edit Playlist',
        'playlist': playlist
    })


@login_required
def delete_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    
    # Only the creator or an admin can delete the playlist
    if not (request.user.is_admin() or playlist.creator == request.user):
        return HttpResponseForbidden("You don't have permission to delete this playlist.")
    
    if request.method == 'POST':
        playlist.delete()
        messages.success(request, 'Playlist deleted successfully!')
        return redirect('playlist_list')
    
    return render(request, 'music_app/playlist_confirm_delete.html', {'playlist': playlist})


@login_required
def rate_music(request, pk):
    if request.method == 'POST':
        music = get_object_or_404(Music, pk=pk)
        rating = request.POST.get('rating')
        
        try:
            rating = int(rating)
            if 1 <= rating <= 5:
                update_user_preferences(request.user, music, rating=rating)
                return JsonResponse({'status': 'success'})
        except (ValueError, TypeError):
            pass
        
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def toggle_favorite(request, pk):
    if request.method == 'POST':
        music = get_object_or_404(Music, pk=pk)
        preference, created = UserMusicPreference.objects.get_or_create(
            user=request.user,
            music=music
        )
        
        preference.favorite = not preference.favorite
        preference.save()
        
        return JsonResponse({
            'status': 'success',
            'is_favorite': preference.favorite
        })
    
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def get_recommendations_view(request):
    limit = int(request.GET.get('limit', 10))
    recommendations = get_recommendations(request.user, limit=limit)
    
    return render(request, 'music_app/recommendations.html', {
        'recommendations': recommendations
    })


@login_required
def favorite_music_list(request):
    # Affiche la liste des musiques favorites de l'utilisateur.
    if not request.user.is_authenticated:
        messages.warning(request, 'You must be logged in to view your favorites.')
        return redirect('login')
    
    favorites = Music.objects.filter(usermusicpreference__user=request.user, usermusicpreference__favorite=True)
    
    return render(request, 'music_app/favorite_music_list.html', {
        'favorites': favorites
    })


def music_statistics(request, pk):
    # Affiche les statistiques détaillées d'une musique
    music = get_object_or_404(Music, pk=pk)
    
    # Vérifier si l'utilisateur est authentifié
    if not request.user.is_authenticated:
        messages.warning(request, 'You must be logged in to view statistics.')
        return redirect('login')
    
    return render(request, 'music_app/music_statistics.html', {
        'music': music
    })