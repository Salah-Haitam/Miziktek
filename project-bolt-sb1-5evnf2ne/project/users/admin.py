from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Artist, Administrator

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'user_type', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type', 'profile_image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Type', {'fields': ('user_type', 'profile_image')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Artist)
admin.site.register(Administrator)