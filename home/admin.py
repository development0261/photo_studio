from django.contrib import admin
from .models import custom_user, Profile, user_detail, application_data, Purchase
from django.contrib.auth.admin import UserAdmin

# Register your models here.


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', "password", 'is_staff', 'confirm_token')


admin.site.register(custom_user, CustomUserAdmin)

admin.site.register(Profile)
admin.site.register(user_detail)
admin.site.register(application_data)
admin.site.register(Purchase)
