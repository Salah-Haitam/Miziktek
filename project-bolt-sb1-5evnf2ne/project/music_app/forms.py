from django import forms
from .models import Music, Playlist


class MusicUploadForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ['title', 'genre', 'release_date', 'audio_file', 'cover_image']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'})
        }


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'music']
        widgets = {
            'music': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PlaylistForm, self).__init__(*args, **kwargs)
        
        if user and user.is_artist():
            # If user is an artist, show only their music
            self.fields['music'].queryset = Music.objects.filter(artist__user=user)
        elif user and user.is_admin():
            # If user is an admin, show all music
            self.fields['music'].queryset = Music.objects.all()
        else:
            # Regular users see all music
            self.fields['music'].queryset = Music.objects.all()