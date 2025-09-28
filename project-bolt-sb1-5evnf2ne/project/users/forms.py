from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Artist


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial=CustomUser.REGULAR_USER
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'user_type']


class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['full_name', 'profile_image']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password']