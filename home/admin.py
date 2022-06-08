from django.contrib import admin
from .models import custom_user
from .models import Profile, user_preference, application_data, Purchase, Tag, Product
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import ModelAdmin
from django.contrib.admin import SimpleListFilter
from datetime import datetime, date, timedelta
from django.utils.html import format_html
import copy

# Register your models here.


class RegisterFilter(SimpleListFilter):
    title = 'Registered Users'
    parameter_name = 'date_joined'

    def lookups(self, request, model_admin):
        return (
            ('Today', 'Today'),
            ('Last 7 days', 'Last 7 days'),
            ('Last 30 days', 'Last 30 days'),
            ('Last 90 days', 'Last 90 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Today':
            return queryset.filter(date_joined__date = date.today())
        if self.value() == 'Last 7 days':
            return queryset.filter(date_joined__gte=datetime.now() - timedelta(days=7), date_joined__lte=datetime.now())
        if self.value() == 'Last 30 days':
            return queryset.filter(date_joined__gte=datetime.now() - timedelta(days=30), date_joined__lte=datetime.now())
        if self.value() == 'Last 90 days':
            return queryset.filter(date_joined__gte=datetime.now() - timedelta(days=90), date_joined__lte=datetime.now())
        if self.value():
            return queryset


class RecentlyRegisterFilter(SimpleListFilter):
    title = 'Recently Registered Users'
    parameter_name = 'last_login'

    def lookups(self, request, model_admin):
        return (
            ('Last 5', 'Last 5'),
            ('Last 10', 'Last 10'),
        )

    def queryset(self, request, queryset):
        def get_data(n):
            Temp = copy.copy(queryset)
            Temp = Temp[:n]
            set_list = custom_user.objects.filter(username__in=Temp)
            return set_list
        if self.value() == 'Last 5':
            return get_data(5)
        if self.value() == 'Last 10':
            return get_data(10)
        if self.value():
            return queryset


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', "password", 'is_staff', 'delete_date', 'confirm_token')
    list_filter = (RegisterFilter, RecentlyRegisterFilter)
    search_list = ('username', 'email', 'first_name', 'last_name') 


class AgeFilter(SimpleListFilter):
    title = 'age'
    parameter_name = 'age'

    def lookups(self, request, model_admin):
        return (
            ('20 - 30', '20 - 30'),
            ('30 - 40', '30 - 40'),
            ('>40', 'Greater than 40'),
        )

    def queryset(self, request, queryset):
        if self.value() == '20 - 30':
            return queryset.filter(dob__gte=datetime.now() - timedelta(days=(365*30)), dob__lt=datetime.now() - timedelta(days=(365*20)))
        if self.value() == '30 - 40':
            return queryset.filter(dob__gte=datetime.now() - timedelta(days=(365*40)), dob__lt=datetime.now() - timedelta(days=(365*30)))
        if self.value() == '>40':
            return queryset.filter(dob__lte=datetime.now() - timedelta(days=(365*40)))
        if self.value():
            return queryset


class PassowordUpdateFilter(SimpleListFilter):
    title = 'Last Password Updated'
    parameter_name = 'pass_update'

    def lookups(self, request, model_admin):
        return (
            ('Today', 'Today'),
            ('Past 7 days', 'Past 7 days'),
            ('This month', 'This month'),
            ('This year', 'This year'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Today':
            return queryset.filter(pass_update__exact=datetime.now())
        if self.value() == 'Past 7 days':
            return queryset.filter(pass_update__gte=datetime.now() - timedelta(days=7), pass_update__lte=datetime.now())
        if self.value() == 'This month':
            return queryset.filter(pass_update__gte=datetime.now() - timedelta(days=30), pass_update__lte=datetime.now())
        if self.value() == 'This year':
            return queryset.filter(pass_update__gte=datetime.now() - timedelta(days=365), pass_update__lte=datetime.now())
        if self.value():
            return queryset


class CustomProfile(admin.ModelAdmin):
    def Profile_Image(self, object):
        if object.profile_image:
            return format_html('<img src="{}" width="40" style="border-radius:50px">'.format(object.profile_image.url))

    list_display = ('username', 'name', 'Profile_Image')
    list_display_links = ('username',)
    list_filter = ("gender", "country", AgeFilter, PassowordUpdateFilter)
    search_fields = ("avatar", "bitmoji", "city", "country", "created_at", "dob", "fb", "gender", "insta", "lat",
                     "long", "mobile", "name", "pass_forgot", "pass_update", "profile_image", "snap", "uid", "updated_at", "website")


class CustomDetails(admin.ModelAdmin):
    list_display = ("username", 'Language')
    search_fields = ("Language", "app_theme", "appearance_mode", "digital_riyals_rewards", "export_quality", "most_used_fonts", "udid", "user_custom_colors",
                     "user_recent_text", "user_stared_Textart", "user_stared_backgrounds", "user_stared_colors", "user_stared_fonts", "user_stared_stickers", "user_stared_templates")


class CustomApps(admin.ModelAdmin):
    list_display = ("username", 'UID')
    search_fields = ("Carrier", "Device_Model", "Device_Storage", "Grace_Period", "Latest_Geolocation",
                     "Purchased_product", "Remaining_grace_period_days", "Total_time_spent", "UID", "aid", "iOS", "inApp_Products")


class CustomPurchase(admin.ModelAdmin):
    search_fields = ["pstatus", ]


class CustomTag(admin.ModelAdmin):
    search_fields = ["tag", ]

class CustomProduct(admin.ModelAdmin):
    search_fields = ["annaulSub", "annaulSubProd", "localeId", "monthlySub", "monthlySubProd", "product", "productID", "productPromo", "promoPrice"]


admin.site.register(custom_user,CustomUserAdmin)
admin.site.register(Profile, CustomProfile)
admin.site.register(user_preference, CustomDetails)
admin.site.register(application_data, CustomApps)
admin.site.register(Purchase, CustomPurchase)
admin.site.register(Tag, CustomTag)
admin.site.register(Product, CustomProduct)

