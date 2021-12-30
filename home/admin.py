from django.contrib import admin
from .models import Registration,custom_user
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', "password", 'is_staff','confirm_token')
admin.site.register(custom_user, CustomUserAdmin)

admin.site.register(Registration)