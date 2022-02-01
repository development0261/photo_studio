from django.contrib import admin
from .models import custom_user, Profile, user_detail, application_data, Purchase
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import ModelAdmin
from django.contrib.admin import SimpleListFilter
import datetime

# Register your models here.
def calculateAge(birthDate):
    today = datetime.date.today()
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
    return age

class CustomUserAdmin(UserAdmin):
    # list_display = ('username', 'email', 'first_name',
    #                 'last_name', "password", 'is_staff', 'confirm_token')
    list_display = ('username', 'email', 'first_name',
                    'last_name', "password", 'is_staff', 'delete_date', 'confirm_token')
    list_filter = ("date_joined",)
admin.site.register(custom_user, CustomUserAdmin)


class CustomProfile(ModelAdmin):
    list_filter = ("gender", "country")

# class AgeFilter(SimpleListFilter):
#     title = 'age' # or use _('country') for translated title
#     parameter_name = 'age'

#     def lookups(self, request, model_admin):
#         dobs = set([row.dob for row in model_admin.model.objects.all()])
#         print(dobs)
#         # return [(row.id, row.name) for row in dobs] + [('AFRICA', 'AFRICA - ALL')]
#         return (
#             ('20 - 30', '20 - 30'),
#             ('30 - 40', '30 - 40'),
#             ('>40', 'Greater than 40'),
#         )

#     def queryset(self, request, queryset):
#         if self.value() == '20 - 30':
#             return queryset.filter(dob__gt = calculateAge())
#         if self.value() == '30 - 40':
#             return queryset.filter(dob__lt = datetime.datetime.now())
#         # if self.value() == '>40':
#         #     return queryset.filter(country__continent='Africa')            
#         if self.value():
#             return queryset

# class youModelAdminClass(admin.ModelAdmin):

#      list_filter = [AgeFilter]
#     #  list_display = ['CustomerValidity']            

admin.site.register(Profile, CustomProfile)



admin.site.register(user_detail)
admin.site.register(application_data)
admin.site.register(Purchase)
