from django.shortcuts import render
from home.models import Product, Profile, Purchase, Tag, application_data, custom_user, user_detail
from home.models import custom_user
from django.apps import apps
from rest_framework.response import Response

# Create your views here.
total_users = custom_user.objects.all()
total_profiles = Profile.objects.all()
total_details = user_detail.objects.all()
total_app_datas = application_data.objects.all()
total_purchases = Purchase.objects.all()
total_tags = Tag.objects.all()
total_products = Product.objects.all()


def models(request):
    app_models = apps.get_app_config('home').get_models()
    home_models = []
    for i in app_models:
        if i.__name__ == "custom_user":
            home_models.append('User')
        else:
            home_models.append(i.__name__)

    app_models = apps.get_app_config('otp_totp').get_models()
    totp = []
    for i in app_models:
        totp.append(i.__name__)
    return {'home_models': home_models, 'totp': totp}


def index(request):
    return render(request, "admin_site/index.html", {'total_users': total_users,
                                                     'total_profiles': total_profiles,
                                                     'total_details': total_details,
                                                     'total_app_datas': total_app_datas,
                                                     'total_purchases': total_purchases,
                                                     'total_tags': total_tags,
                                                     'total_products': total_products,
                                                     })


def user_model(request):
    profiles = custom_user.objects.get(username='admin').profile
    app_datas = custom_user.objects.get(username='admin').application_data
    details = custom_user.objects.get(username='admin').user_detail
    products = custom_user.objects.get(username='admin').product
    purchases = custom_user.objects.get(username='admin').purchase
    tags = custom_user.objects.get(username='admin').tag
    data = {"app_datas": app_datas,
            "details": details,
            "products": products,
            "profiles": profiles,
            "purchases": purchases,
            "tags": tags
            }
    return render(request, "admin_site/user_model.html", {'total_users': total_users, 'data':data})


def profile_model(request):
    return render(request, "admin_site/profile_model.html", {'total_profiles': total_profiles})


def user_deatils_model(request):
    return render(request, "admin_site/user_deatils_model.html", {'total_details': total_details})


def app_data_model(request):
    return render(request, "admin_site/app_data_model.html", {'total_app_datas': total_app_datas})


def purchase_model(request):
    return render(request, "admin_site/purchase_model.html", {'total_purchases': total_purchases})


def tag_model(request):
    return render(request, "admin_site/tag_model.html", {'total_tags': total_tags})


def product_model(request):
    return render(request, "admin_site/product_model.html", {'total_products': total_products})

import json
from django.http.response import JsonResponse
# from rest_framework import serializers
from django.core import serializers
def view_profile(request,info):
    infolist = info.replace(" ","").split('-')
    obj = Profile.objects.filter(name=infolist[2])
    data = serializers.serialize("json", obj)
    data = json.loads(data[1:-1])
    return JsonResponse({"res":data})