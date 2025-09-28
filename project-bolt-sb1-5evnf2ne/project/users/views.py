from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ArtistProfileForm, UserLoginForm
from music_app.models import Music, Playlist


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if user.is_artist():
        # For artist dashboard
        music_list = Music.objects.filter(artist__user=user)
        playlists = Playlist.objects.filter(creator=user)
        context.update({
            'music_list': music_list,
            'playlists': playlists
        })
        return render(request, 'users/artist_dashboard.html', context)
    
    elif user.is_admin():
        # For admin dashboard
        all_music = Music.objects.all()
        all_playlists = Playlist.objects.all()
        all_users = user.__class__.objects.all()
        context.update({
            'all_music': all_music,
            'all_playlists': all_playlists,
            'all_users': all_users
        })
        return render(request, 'users/admin_dashboard.html', context)
    
    else:
        # For regular user dashboard
        playlists = Playlist.objects.filter(creator=user)
        recent_music = Music.objects.all().order_by('-release_date')[:10]
        context.update({
            'playlists': playlists,
            'recent_music': recent_music
        })
        return render(request, 'users/user_dashboard.html', context)


@login_required
def profile(request):
    user = request.user
    
    if user.is_artist() and request.method == 'POST':
        form = ArtistProfileForm(request.POST, request.FILES, instance=user.artist_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    
    elif user.is_artist():
        form = ArtistProfileForm(instance=user.artist_profile)
        return render(request, 'users/profile.html', {'form': form})
    
    return render(request, 'users/profile.html')