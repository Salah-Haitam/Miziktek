from django.urls import path
from . import views

urlpatterns = [
    # Recommendations
    path('recommendations/', views.get_recommendations_view, name='recommendations'),
    
    # User interactions
    path('music/<int:pk>/rate/', views.rate_music, name='rate_music'),
    path('music/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_music_list, name='favorite_list'),

    path('', views.home, name='home'),
    path('music/', views.music_list, name='music_list'),
    path('music/<int:pk>/', views.music_detail, name='music_detail'),
    path('music/<int:pk>/statistics/', views.music_statistics, name='music_statistics'),
    path('music/upload/', views.upload_music, name='upload_music'),
    path('music/edit/<int:pk>/', views.edit_music, name='edit_music'),
    path('music/delete/<int:pk>/', views.delete_music, name='delete_music'),
    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlist/<int:pk>/', views.playlist_detail, name='playlist_detail'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('playlist/edit/<int:pk>/', views.edit_playlist, name='edit_playlist'),
    path('playlist/delete/<int:pk>/', views.delete_playlist, name='delete_playlist'),
]