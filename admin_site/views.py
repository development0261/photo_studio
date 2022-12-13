from datetime import date, datetime, timedelta
import copy
from urllib import response
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import redirect, render
from home.models import Product, Profile, Purchase, Tag, application_data, application_data_noauth, custom_user, user_preference
from home.models import custom_user
from django.apps import apps
from rest_framework.response import Response
import json
from django.http.response import JsonResponse
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
import string
import random
import re
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import base64
from django.core.paginator import Paginator
from django.db.models import Q
import csv
from django.apps import apps
import requests, json


punctuation = "!#$%&()*+, -./:;<=>?@[\]^_`{|}~"
# reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#$%&*+,-./:;<=>?@\^_`|~])[A-Za-z\d!#$%&*+,-./:;<=>?@\^_`|~]{6,20}$"
reg = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{6,20}$"

# Create your views here.

# login for admin
def loginprocess(request):
    if 'otpSubmit' in request.POST:
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = custom_user.objects.get(email=email)
            if user.is_superuser:
                if user.check_password(password):
                    otp_gen = string.digits
                    confirm_otp = ''.join(random.choice(otp_gen) for i in range(6))
                    send_mail(
                        subject="OTP Verification",
                        message="Your OTP is  :  " + confirm_otp,
                        from_email='no-reply@3rabapp.com',
                        recipient_list=[email],
                        fail_silently=False,
                    )
                    user.confirm_token = confirm_otp
                    user.save()
                    messages.success(request, 'Check your mail Inbox.')
                    return redirect('login')
                else:
                    messages.error(request, 'Please check your password!!!')
                    return redirect("login")
            else:
                messages.error(request, 'You arenot admin user!!!')
                return redirect("login")
        except Exception as e:
            messages.error(request, 'Please check your email!!!')
            return redirect("login")

    if 'FinalSubmit' in request.POST:
        otp = request.POST['otp']
        email = request.POST['email']
        obj = custom_user.objects.get(email=email)
        if obj.confirm_token == otp:
            login(request, obj)
            messages.success(request, 'Login Successfully.')
            return redirect("index")
        else:
            messages.error(request, 'Please check your otp!!!')
            return redirect("login")

    return render(request, 'admin_site/login.html')

# get models data for home page
def models(request):
    app_models = apps.get_app_config('home').get_models()
    home_models = []
    for i in app_models:
        if i.__name__ == "custom_user":
            pass
        elif i.__name__ == 'user_preference':
            home_models.append('User Preference')
        elif i.__name__ == 'application_data':
            home_models.append('Application Data')
        else:
            home_models.append(i.__name__)
    return {'home_models': home_models}

# get all models data
def all_table_data():
    admins = custom_user.objects.filter(is_superuser=True)
    locals = custom_user.objects.filter(is_superuser=False)
    total_profiles = Profile.objects.all().order_by('-created_at')
    total_details = user_preference.objects.all()
    total_app_datas = application_data.objects.all()
    total_no_auth_app_datas = application_data_noauth.objects.all()
    total_purchases = Purchase.objects.all()
    total_tags = Tag.objects.all()
    total_products = Product.objects.all()
    all_data = {'admins':admins, 'locals':locals, 'total_profiles':total_profiles, 'total_details':total_details, 'total_app_datas':total_app_datas, 'total_no_auth_app_datas':total_no_auth_app_datas, 'total_purchases':total_purchases, 'total_tags':total_tags, 'total_products':total_products}
    return all_data

# for index page of admin panel
def index(request):
    if request.user.is_authenticated:
        
        return render(request, "admin_site/index.html", {'total_admins': all_table_data()['admins'],
                                                         'total_locals': all_table_data()['locals'],
                                                         'total_profiles': all_table_data()['total_profiles'],
                                                         'total_details': all_table_data()['total_details'],
                                                         'total_app_datas': all_table_data()['total_app_datas'],
                                                         'total_no_auth_app_datas': all_table_data()['total_no_auth_app_datas'],
                                                         'total_purchases': all_table_data()['total_purchases'],
                                                         'total_tags': all_table_data()['total_tags'],
                                                         'total_products': all_table_data()['total_products'],
                                                         })
    else:
        return redirect("login")

# admin users
def admin_user(request):
    if request.user.is_authenticated:
        admins = custom_user.objects.filter(is_superuser=True).order_by('-date_joined')
        return render(request, "admin_site/admin_user.html", {'admins': admins})
    else:
        return redirect("login")

# app users
def app_user(request):
    if request.user.is_authenticated:
        locals = custom_user.objects.filter(is_superuser=False).order_by('-date_joined')

        if 'search' in request.GET:
            searchvalue = request.GET['search']
            locals = custom_user.objects.filter(
                                Q(username__icontains=searchvalue) |
                                Q(first_name__icontains=searchvalue) |
                                Q(last_name__icontains=searchvalue) |
                                Q(email__icontains=searchvalue)
                            )

        if 'datefilter' in request.GET:
            val = request.GET['datefilter']
            if val == 'today':
                locals = locals.filter(date_joined__date=date.today())
            if val == 'seven':
                locals = locals.filter(date_joined__gte=datetime.now(
                ) - timedelta(days=7), date_joined__lte=datetime.now())
            if val == 'thirty':
                locals = locals.filter(date_joined__gte=datetime.now(
                ) - timedelta(days=30), date_joined__lte=datetime.now())
            if val == 'ninety':
                locals = locals.filter(date_joined__gte=datetime.now(
                ) - timedelta(days=90), date_joined__lte=datetime.now())

            if val == 'five':
                Temp = copy.copy(locals)
                locals = Temp[:5]
            if val == 'ten':
                Temp = copy.copy(locals)
                locals = Temp[:10]

        if 'show' in request.GET:
            showval = request.GET['show']
            p = Paginator(locals, showval)
        else:
            p = Paginator(locals, 10)
            
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)

        return render(request, "admin_site/user_model.html", {'locals': page_obj})
    else:
        return redirect("login")

#export data
def export_excel(request):
    if 'data' in request.GET:
        model_name = request.GET['data']
        Model = apps.get_model('home', model_name)
        print("model_name",model_name)
        
    smallest_age_record = ""
    biggest_age_record = ""
    filter_mobile_val = ""
    latitude = ""
    longitude = ""

    result_queryset = Model.objects.all().order_by('-created_at')
    
    if 'search' in request.GET:   
        if request.GET['search']:
            searchvalue = request.GET['search']
            if model_name == "Profile":
                result_queryset = Model.objects.filter(
                                    Q(name__icontains=searchvalue) |
                                    Q(mobile__icontains=searchvalue) |
                                    Q(gender__icontains=searchvalue) |
                                    Q(city__icontains=searchvalue) |
                                    Q(country__icontains=searchvalue)
                                )
            elif model_name == "Product":
                result_queryset = Model.objects.filter(
                                Q(productID__icontains=searchvalue) |
                                Q(product__icontains=searchvalue) |
                                Q(productPromo__icontains=searchvalue) |
                                Q(promoPrice__icontains=searchvalue) |
                                Q(annaulSubProd__icontains=searchvalue) |
                                Q(annaulSub__icontains=searchvalue) |
                                Q(monthlySubProd__icontains=searchvalue) |
                                Q(monthlySub__icontains=searchvalue) |
                                Q(localeId__icontains=searchvalue)
                )
            elif model_name =="application_data_noauth":
                result_queryset = Model.objects.filter(
                    Q(inApp_Products=searchvalue))
                
            elif model_name =="Purchase":
                result_queryset = Model.objects.filter(
                    Q(product=searchvalue)|
                    Q(pstatus=searchvalue)|                   
                    Q(subscription_type=searchvalue)                    
                    )
            elif model_name =="Tag":
                result_queryset = Model.objects.filter(
                    Q(username=searchvalue)|
                    Q(tag=searchvalue)                    
                    )
            elif model_name =="application_data":
                result_queryset = Model.objects.filter(
                    Q(inApp_Products=searchvalue)|
                    Q(Device_Model=searchvalue)|                    
                    Q(operating_system=searchvalue)|                    
                    Q(Device_Storage=searchvalue)|                    
                    Q(Purchased_product=searchvalue)                 
                    )
            elif model_name =="user_preference":
                result_queryset = Model.objects.filter(
                    Q(export_quality=searchvalue)|
                    Q(username=searchvalue)|                    
                    Q(signature=searchvalue)              
                    )

    if 'filter_mobile' in request.GET:
        if request.GET['filter_mobile']:
            searchvalue = request.GET['filter_mobile']
            filter_mobile_val = searchvalue
            result_queryset = result_queryset.filter(Q(mobile__icontains=searchvalue))

    if 'gender' in request.GET:
        if request.GET['gender']:
            val = request.GET['gender']
            if val == 'All':
                result_queryset = result_queryset.all()
            if val == 'Male':
                result_queryset = result_queryset.filter(gender__iexact="Male")
            if val == 'Female':
                result_queryset = result_queryset.filter(gender__iexact="Female")
            if val == 'Other':
                result_queryset = result_queryset.filter(gender__iexact="Other")

    if 'age' in request.GET:
        if request.GET['age']:
            val = request.GET['age']
            if val == 'All':
                result_queryset = result_queryset.all()
            if val == 'twenty':
                result_queryset = result_queryset.filter(dob__gte=datetime.now(
                ) - timedelta(days=(365*30)), dob__lt=datetime.now() - timedelta(days=(365*20)))
            if val == 'thirty':
                result_queryset = result_queryset.filter(dob__gte=datetime.now(
                ) - timedelta(days=(365*40)), dob__lt=datetime.now() - timedelta(days=(365*30)))
            if val == 'greater':
                result_queryset = result_queryset.filter(
                    dob__lte=datetime.now() - timedelta(days=(365*40)))

    if 'city' in request.GET:
        if request.GET['city']:
            val = request.GET['city']
            cities = Profile.objects.values('city').distinct()
            city_list1 = []
            for i in cities:
                if i != 'None' or i !='none':
                    city_list1.append(str(i['city']).upper())
            city_list1 = set(city_list1)
            city_list = []
            for i in city_list1:
                if i=='NONE':
                    pass
                else:
                    city_list.append(i)

            if val == 'All':
                result_queryset = result_queryset.all()
            for i in city_list:
                if i == val:
                    result_queryset = result_queryset.filter(city__iexact=val)

    if 'country' in request.GET:
        if request.GET['country']:
            val = request.GET['country']
            countries = Profile.objects.values('country').distinct()
            country_list1 = []
            for i in countries:
                if i != 'None' or i !='none':
                    country_list1.append(str(i['country']).upper())
            country_list1 = set(country_list1)
            country_list = []
            for i in country_list1:
                if i=='NONE':
                    pass
                else:
                    country_list.append(i)
            if val == 'All':
                result_queryset = result_queryset.all()
            for i in country_list:
                if i == val:
                    result_queryset = result_queryset.filter(country__iexact=val)                  

    if 'password_update' in request.GET:
        if request.GET['password_update']:
            val = request.GET['password_update']
            if val == 'All':
                result_queryset = result_queryset.all()
            if val == 'today':
              result_queryset = result_queryset.filter(
                    pass_update__exact=datetime.now())
            if val == 'seven':
                result_queryset = result_queryset.filter(pass_update__gte=datetime.now(
                ) - timedelta(days=7), pass_update__lte=datetime.now())
            if val == 'month':
                result_queryset = result_queryset.filter(pass_update__gte=datetime.now(
                ) - timedelta(days=30), pass_update__lte=datetime.now())
            if val == 'year':
                result_queryset = result_queryset.filter(pass_update__gte=datetime.now(
                ) - timedelta(days=365), pass_update__lte=datetime.now())

    if 'fromtodate' in request.GET:
        if request.GET['fromtodate']:
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']

            format_data = "%Y-%m-%d %H:%M:%S"
            if start_date:
                start_date = datetime.strptime(start_date+" 00:00:00", format_data)
            if end_date:
                end_date = datetime.strptime(end_date+" 23:59:59", format_data)

            if start_date or end_date:
                result_queryset = result_queryset.filter(created_at__gte = start_date, created_at__lte = end_date)

    if 'agefilter' in request.GET:
        if request.GET['agefilter']:
            start_age = request.GET['start_age']
            end_age = request.GET['end_age']

            if not start_age:
                start_age = 0

            if len(end_age) == 0:
                result_queryset = result_queryset.filter(dob__lt=datetime.now() - timedelta(days=(365*int(start_age))))
            else:
                result_queryset = result_queryset.filter(dob__gte=datetime.now(
                    ) - timedelta(days=(365*int(end_age))), dob__lt=datetime.now() - timedelta(days=(365*int(start_age))))

    if 'radius' in request.GET:
        if request.GET['radius']:
            latitude = request.GET['latitude']
            longitude = request.GET['longitude']
            result_queryset = result_queryset.filter(Q(lat__icontains = latitude) |  Q(long__icontains = longitude))

    response = HttpResponse(content_type='application/ms-excel')
    response = HttpResponse()
    response['Content-Disposition'] = f'attachment;filename={model_name}.csv'
    writer = csv.writer(response)

    if 'cols' in request.GET:
        cols = request.GET['cols']
        cols_list = cols.split(",")
        
        all = {}
        for i in cols_list:
            info = Model.objects.only(i)
            all[i] = info
        
        writer.writerow(cols_list)
        for i,j in all.items():
            for obj in j:
                columns_dict = {}
                for field in cols_list:

                    if field == "profile_image":
                        if getattr(obj, field):
                            columns_dict[field] = 'http://127.0.0.1:8001/media/' + str(getattr(obj, field))
                        else:
                            columns_dict[field] = getattr(obj, field)
                    else:
                        columns_dict[field] = getattr(obj, field)
                writer.writerow(list(columns_dict.values()))
            break
        return response

    # if 'users' in request.GET:
    #     users = request.GET['users']
    #     users_list = users.split(",")
    #     res = [int(i) for i in users_list]
    #     result_queryset = Profile.objects.filter(pk__in = res)

    opts = result_queryset.model._meta
    field_names = [field.name for field in opts.fields]
    writer.writerow(field_names)
    for obj in result_queryset:
        temp_list = []
        for field in field_names:
            if field == "profile_image":
                if getattr(obj, field):
                    temp_list.append('http://127.0.0.1:8001/media/' + str(getattr(obj, field)))
                else:
                    temp_list.append(getattr(obj, field))
            else:
                temp_list.append(getattr(obj, field))
        writer.writerow(temp_list)
    return response

# profile model data
def profile_model(request):
    if request.user.is_authenticated:
        countries = Profile.objects.values('country').distinct()
        country_list1 = []
        for i in countries:
            if i != 'None' or i !='none':
                country_list1.append(str(i['country']).upper())
        country_list1 = set(country_list1)
        country_list = []
        for i in country_list1:
            if i=='NONE':
                pass
            else:
                country_list.append(i)

        cities = Profile.objects.values('city').distinct()
        city_list1 = []
        for i in cities:
            if i != 'None' or i !='none':
                city_list1.append(str(i['city']).upper())
        city_list1 = set(city_list1)
        city_list = []
        for i in city_list1:
            if i=='NONE':
                pass
            else:
                city_list.append(i)

        total_profiles = Profile.objects.all().order_by('-created_at')

        first_record = total_profiles[0].created_at
        last_record = total_profiles.reverse()[0].created_at
        first_record = first_record.strftime("%Y-%m-%d")
        last_record = last_record.strftime("%Y-%m-%d")

        smallest_age_record = ""
        biggest_age_record = ""
        filter_mobile_val = ""
        latitude = ""
        longitude = ""
        
        if 'search' in request.GET:
            
            searchvalue = request.GET['search']
            total_profiles = Profile.objects.filter(
                                Q(name__icontains=searchvalue) |
                                Q(mobile__icontains=searchvalue) |
                                Q(gender__icontains=searchvalue) |
                                Q(city__icontains=searchvalue) |
                                Q(country__icontains=searchvalue)
                            )

        if 'filter_mobile' in request.GET:
            searchvalue = request.GET['filter_mobile']
            filter_mobile_val = searchvalue
            total_profiles = Profile.objects.filter(Q(mobile__icontains=searchvalue))

        if 'gender' in request.GET:
            val = request.GET['gender']
            if val == 'All':
                total_profiles = total_profiles.all()
            if val == 'Male':
                total_profiles = total_profiles.filter(gender__iexact="Male")
            if val == 'Female':
                total_profiles = total_profiles.filter(gender__iexact="Female")
            if val == 'Other':
                total_profiles = total_profiles.filter(gender__iexact="Other")

        if 'age' in request.GET:
            val = request.GET['age']
            if val == 'All':
                total_profiles = total_profiles.all()
            if val == 'twenty':
                total_profiles = total_profiles.filter(dob__gte=datetime.now(
                ) - timedelta(days=(365*30)), dob__lt=datetime.now() - timedelta(days=(365*20)))
            if val == 'thirty':
                total_profiles = total_profiles.filter(dob__gte=datetime.now(
                ) - timedelta(days=(365*40)), dob__lt=datetime.now() - timedelta(days=(365*30)))
            if val == 'greater':
                total_profiles = total_profiles.filter(
                    dob__lte=datetime.now() - timedelta(days=(365*40)))

        if 'city' in request.GET:
            val = request.GET['city']
            if val == 'All':
                total_profiles = total_profiles.all()
            for i in city_list:
                if i == val:
                    total_profiles = total_profiles.filter(city__iexact=val)

        if 'country' in request.GET:
            val = request.GET['country']
            if val == 'All':
                total_profiles = total_profiles.all()
            for i in country_list:
                if i == val:
                    total_profiles = total_profiles.filter(country__iexact=val)                  

        if 'password_update' in request.GET:
            val = request.GET['password_update']
            if val == 'All':
                total_profiles = total_profiles.all()
            if val == 'today':
              total_profiles = total_profiles.filter(
                    pass_update__exact=datetime.now())
            if val == 'seven':
                total_profiles = total_profiles.filter(pass_update__gte=datetime.now(
                ) - timedelta(days=7), pass_update__lte=datetime.now())
            if val == 'month':
                total_profiles = total_profiles.filter(pass_update__gte=datetime.now(
                ) - timedelta(days=30), pass_update__lte=datetime.now())
            if val == 'year':
                total_profiles = total_profiles.filter(pass_update__gte=datetime.now(
                ) - timedelta(days=365), pass_update__lte=datetime.now())

        if 'fromtodate' in request.GET:
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']

            format_data = "%Y-%m-%d %H:%M:%S"
            start_date = datetime.strptime(start_date+" 00:00:00", format_data)
            end_date = datetime.strptime(end_date+" 23:59:59", format_data)

            total_profiles = total_profiles.filter(created_at__gte = start_date, created_at__lte = end_date)

            last_record = start_date.strftime("%Y-%m-%d")
            first_record = end_date.strftime("%Y-%m-%d")

        if 'agefilter' in request.GET:
            start_age = request.GET['start_age']
            end_age = request.GET['end_age']

            if not start_age:
                start_age = 0

            if len(end_age) == 0:
                total_profiles = total_profiles.filter(dob__lt=datetime.now() - timedelta(days=(365*int(start_age))))
            else:
                total_profiles = total_profiles.filter(dob__gte=datetime.now(
                    ) - timedelta(days=(365*int(end_age))), dob__lt=datetime.now() - timedelta(days=(365*int(start_age))))

            smallest_age_record = start_age
            biggest_age_record = end_age

        if 'radius' in request.GET:
            latitude = request.GET['latitude']
            longitude = request.GET['longitude']
            total_profiles = total_profiles.filter(Q(lat__icontains = latitude) |  Q(long__icontains = longitude))

        if 'show' in request.GET:
            showval = request.GET['show']
            p = Paginator(total_profiles, showval)
        else:
            p = Paginator(total_profiles, 10)
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)

        # print(total_profiles)
        # print(page_obj)
        # for i in page_obj:
        #     print(i)

        return render(request, "admin_site/profile_model.html", {'total_profiles': page_obj, 'total_records':len(page_obj), 'country_list':country_list, 'city_list':city_list, "first_record": first_record, "last_record": last_record, "smallest_age_record":smallest_age_record, "biggest_age_record":biggest_age_record, "filter_mobile_val":filter_mobile_val, "searched_lat":latitude, "searched_long":longitude})
    else:
        return redirect("login")

# preferences model data
def user_preference_model(request):
    if request.user.is_authenticated:
        total_details = user_preference.objects.all().order_by('-created_at')

        if 'search' in request.GET:
            searchvalue = request.GET['search']
            total_details = user_preference.objects.filter(
                                Q(export_quality__icontains=searchvalue) |
                                Q(Language__icontains=searchvalue) |
                                Q(user_stared_templates__icontains=searchvalue) |
                                Q(user_stared_backgrounds__icontains=searchvalue) |
                                Q(user_stared_stickers__icontains=searchvalue) |
                                Q(user_stared_Textart__icontains=searchvalue) |
                                Q(user_stared_colors__icontains=searchvalue) |
                                Q(user_stared_fonts__icontains=searchvalue) |
                                Q(most_used_fonts__icontains=searchvalue) |
                                Q(user_custom_colors__icontains=searchvalue) |
                                Q(user_recent_text__icontains=searchvalue) |
                                Q(appearance_mode__icontains=searchvalue) |
                                Q(app_theme__icontains=searchvalue)                                

            )

        if 'show' in request.GET:
            showval = request.GET['show']
            p = Paginator(total_details, showval)
        else:
            p = Paginator(total_details, 10)
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)

        return render(request, "admin_site/user_preferences_model.html", {'total_details': page_obj})
    else:
        return redirect("login")

# application model data
def app_data_model(request):
    if request.user.is_authenticated:
        total_app_datas = application_data.objects.all().order_by('-created_at')

        if 'search' in request.GET:
            searchvalue = request.GET['search']
            total_app_datas = application_data.objects.filter(
                                Q(inApp_Products__icontains=searchvalue) |
                                Q(Purchased_product__icontains=searchvalue) |
                                Q(Device_Model__icontains=searchvalue) |
                                Q(operating_system__icontains=searchvalue) |
                                Q(Device_Storage__icontains=searchvalue) |
                                Q(Carrier__icontains=searchvalue) |
                                Q(Grace_Period__icontains=searchvalue) |
                                Q(Total_time_spent__icontains=searchvalue) |
                                Q(Push_Notification_token__icontains=searchvalue)|
                                Q(username__username__icontains=searchvalue)
            )
        if 'show' in request.GET:
            showval = request.GET['show']
            p = Paginator(total_app_datas, showval)
        else:
            p = Paginator(total_app_datas, 10)
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)

        return render(request, "admin_site/app_data_model.html", {'total_app_datas': page_obj})
    else:
        return redirect("login")

# no auth application model data
def no_auth_app_data_model(request):
    if request.user.is_authenticated:
        total_no_auth_app_datas = application_data_noauth.objects.all().order_by('-created_at')

        if 'search' in request.GET:
            searchvalue = request.GET['search']
            
            total_no_auth_app_datas = application_data_noauth.objects.filter(
                                Q(UID=searchvalue) |
                                Q(inApp_Products__icontains=searchvalue) |
                                Q(Purchased_product__icontains=searchvalue) |
                                Q(Device_Model__icontains=searchvalue) |
                                Q(operating_system__icontains=searchvalue) |
                                Q(Device_Storage__icontains=searchvalue) |
                                Q(Carrier__icontains=searchvalue) |
                                Q(Grace_Period__icontains=searchvalue) |
                                Q(Total_time_spent__icontains=searchvalue) |
                                Q(Push_Notification_token__icontains=searchvalue)
            )
        if 'show' in request.GET:
            showval = request.GET['show']
            p = Paginator(total_no_auth_app_datas, showval)
        else:
            p = Paginator(total_no_auth_app_datas, 10)
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)

        return render(request, "admin_site/app_data_no_auth_model.html", {'total_no_auth_app_datas': page_obj})
    else:
        return redirect("login")

# purchase model data
def purchase_model(request):
    print("Purchase Model")
    if request.user.is_authenticated:
        total_purchases = Purchase.objects.all().order_by('-created_at')
        
        if 'search' in request.GET:
            print("Search")
            searchvalue = request.GET['search']
            total_purchases = Purchase.objects.filter(
                                Q(pstatus__icontains=searchvalue) |
                                Q(subscription_type__icontains=searchvalue) |
                                Q(username__username__icontains=searchvalue)
            )

        if 'show' in request.GET:
            showval = request.GET['show']
            p = Paginator(total_purchases, showval)
        else:
            p = Paginator(total_purchases, 10)
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)
        
        return render(request, "admin_site/purchase_model.html", {'total_purchases': page_obj})
    else:
        return redirect("login")

# tag model data
def tag_model(request):
    if request.user.is_authenticated:
        total_tags = Tag.objects.all().order_by('-created_at')

        if 'search' in request.GET:
            searchvalue = request.GET['search']
            total_tags = Tag.objects.filter(
                                Q(tag__icontains=searchvalue)
            )

        if 'show' in request.GET:
            showval = request.GET['show']
            p = Paginator(total_tags, showval)
        else:
            p = Paginator(total_tags, 10)
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)

        return render(request, "admin_site/tag_model.html", {'total_tags': page_obj})
    else:
        return redirect("login")

# product model data
def product_model(request):
    if request.user.is_authenticated:
        total_products = Product.objects.all().order_by('-created_at')

        if 'search' in request.GET:
            searchvalue = request.GET['search']
            
            total_products = Product.objects.filter(
                                Q(productID__icontains=searchvalue) |
                                Q(product__icontains=searchvalue) |
                                Q(productPromo__icontains=searchvalue) |
                                Q(promoPrice__icontains=searchvalue) |
                                Q(annaulSubProd__icontains=searchvalue) |
                                Q(annaulSub__icontains=searchvalue) |
                                Q(monthlySubProd__icontains=searchvalue) |
                                Q(monthlySub__icontains=searchvalue) |
                                Q(localeId__icontains=searchvalue)
            )

        if 'show' in request.GET:
            showval = request.GET['show']
            p = Paginator(total_products, showval)
        else:
            p = Paginator(total_products, 10)
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)

        return render(request, "admin_site/product_model.html", {'total_products': page_obj})
    else:
        return redirect("login")

# View specific model data start---------\
def view_profile(request, info):
    if request.user.is_authenticated:
        infolist = info.replace(" ", "").split('-')
        user_obj = custom_user.objects.get(username=infolist[1])
        obj = Profile.objects.filter(username=user_obj)
        data = serializers.serialize("json", obj)
        data = json.loads(data[1:-1])
        return JsonResponse({"res": data})
    else:
        return redirect("login")

def specific_purchase(request, info):
    print("Specific Purchase")
    if request.user.is_authenticated:
        obj = Purchase.objects.filter(purchase_id=int(info))
        data = serializers.serialize("json", obj)
        data = json.loads(data[1:-1])
        return JsonResponse({"res": data})
    else:
        return redirect("login")

def view_purchases(request, info):
    
    print("View Purchase")
    if request.user.is_authenticated:
        infolist = info.replace(" ", "").split('-')
        user_obj = custom_user.objects.get(username=infolist[1])
        obj = Purchase.objects.filter(username=user_obj.id)
        data = []
        for i in obj:
            data.append(i.product)
        data = serializers.serialize("json", data)
        data = json.loads(data)
        return JsonResponse({"res": data})
    else:
        return redirect("login")

def specific_product(request, info):
    if request.user.is_authenticated:
        infolist = info.split(' ')
        obj = Product.objects.filter(product=infolist[0])
        data = serializers.serialize("json", obj)
        data = json.loads(data[1:-1])
        return JsonResponse({"res": data})
    else:
        return redirect("login")


def view_tag(request, info):
    if request.user.is_authenticated:
        infolist = info.replace(" ", "").split('-')
        obj = custom_user.objects.get(username=infolist[1])
        obj1 = Tag.objects.filter(username=obj.id)
        data = serializers.serialize("json", obj1)
        data = json.loads(data)
        final = []
        for i in data:
            final.append(i['fields']['tag'])
        return JsonResponse({"res": final})
    else:
        return redirect("login")


def view_user_preference(request, info):
    if request.user.is_authenticated:
        infolist = info.replace(" ", "").split('-')
        obj = user_preference.objects.filter(udid=infolist[2])
        data = serializers.serialize("json", obj)
        data = json.loads(data[1:-1])
        return JsonResponse({"res": data})
    else:
        return redirect("login")


def view_product(request, info):
    if request.user.is_authenticated:
        infolist = info.replace(" ", "").split('-')
        obj = Product.objects.filter(PID=infolist[1])
        data = serializers.serialize("json", obj)
        data = json.loads(data[1:-1])
        return JsonResponse({"res": data})
    else:
        return redirect("login")


def view_app_data(request, info):
    if request.user.is_authenticated:
        infolist = info.replace(" ", "").split('-')
        obj = application_data.objects.filter(UID=infolist[2])
        data = serializers.serialize("json", obj)
        data = json.loads(data[1:-1])
        return JsonResponse({"res": data})
    else:
        return redirect("login")

# def view_app_data_no_auth(request, info):
#     if request.user.is_authenticated:
#         infolist = info.replace(" ", "").split('-')
#         obj = application_data_noauth.objects.filter(UID=infolist[1])
#         data = serializers.serialize("json", obj)
#         data = json.loads(data[1:-1])
#         return JsonResponse({"res": data})
#     else:
#         return redirect("login")    

def view_app_data_without_auth(request, info):
    if request.user.is_authenticated:
        print(info)
        infolist = info.replace(" ", "").split('-')
        print(infolist)
        obj = application_data_noauth.objects.filter(UID=infolist[1])
        print(obj)
        data = serializers.serialize("json", obj)
        data = json.loads(data[1:-1])
        return JsonResponse({"res": data})
    else:
        return redirect("login")        

# View specific model data end---------/

# delete specific model data start---------\
def delete_user(request, para=None):
    if request.user.is_authenticated:
        modal_id = para.split(" ")
        obj = custom_user.objects.get(id=int(modal_id[1]))
        if modal_id[0] == str(obj):
            obj.delete()
        return redirect('custom_user')
    else:
        return redirect("login")


def delete_profile(request, para=None):
    if request.user.is_authenticated:
        modal_id = para.split(" ")
        obj = Profile.objects.get(uid=int(modal_id[1]))
        obj.delete()
        return redirect('Profile')
    else:
        return redirect("login")


def delete_details(request, para=None):
    if request.user.is_authenticated:
        modal_id = para.split(" ")
        obj = user_preference.objects.get(udid=int(modal_id[1]))
        obj.delete()
        return redirect('user_preference')
    else:
        return redirect("login")


def delete_app_data(request, para=None):
    if request.user.is_authenticated:
        modal_id = para.split(" ")
        obj = application_data.objects.get(aid=int(modal_id[1]))
        obj.delete()
        return redirect('application_data')
    else:
        return redirect("login")

def delete_no_auth_app_data(request, para=None):
    if request.user.is_authenticated:
        modal_id = para.split(" ")
        obj = application_data_noauth.objects.get(aid=int(modal_id[1]))
        obj.delete()
        return redirect('no_auth_app_data_model')
    else:
        return redirect("login")        


def delete_purchase(request, para=None):
    if request.user.is_authenticated:
        modal_id = para.split(" ")
        obj = Purchase.objects.get(pid=int(modal_id[1]))
        obj.delete()
        return redirect('Purchase')
    else:
        return redirect("login")


def delete_tag(request, para=None):
    if request.user.is_authenticated:
        modal_id = para.split(" ")
        obj = Tag.objects.get(id=int(modal_id[1]))
        obj.delete()
        return redirect('Tag')
    else:
        return redirect("login")


def delete_product(request, para=None):
    if request.user.is_authenticated:
        modal_id = para.split(" ")
        obj = Product.objects.get(PID=int(modal_id[1]))
        obj.delete()
        return redirect('Product')
    else:
        return redirect("login")

# delete specific model data end---------/

# edit specific model data start---------\
def user_edit(request, para):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            email = request.POST['email']
            active = request.POST.get('active_user')
            staff = request.POST.get('staff_user')
            
            obj = custom_user.objects.get(username=username)
            
            if obj.email != email:
                if custom_user.objects.filter(email=email):
                    messages.error(request, 'Email already Exists!!!')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                        
            obj.first_name = firstname
            obj.last_name = lastname
            obj.email = email
            if active == "on":
                obj.is_active = True
            else:
                obj.is_active = False

            if staff == "on":
                obj.is_staff = True
            else:
                obj.is_staff = False
            obj.save()

            return redirect('custom_user')

        elif request.method == "GET":
            modal_id = para.split(" ")
            obj = custom_user.objects.filter(username=modal_id[0])
            data = serializers.serialize("json", obj)
            data = json.loads(data)
            res = []
            for i in data:
                res.append(i['fields'])
            return render(request, 'admin_site/edit_models.html', {"result": res})
    else:
        return redirect("login")


def admin_edit(request, para):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            email = request.POST['email']
            obj = custom_user.objects.get(username=username)
            if obj.email != email:
                if custom_user.objects.filter(email=email):
                    messages.error(request, 'Email already Exists!!!')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            obj.first_name = firstname
            obj.last_name = lastname
            obj.email = email
            obj.save()

            return redirect('adminusers')

        elif request.method == "GET":
            modal_id = para.split(" ")
            print("->",modal_id)
            obj = custom_user.objects.filter(username=modal_id[0])
            data = serializers.serialize("json", obj)
            data = json.loads(data)
            res = []
            for i in data:
                res.append(i['fields'])
            return render(request, 'admin_site/admin_edit.html', {"result": res})
    else:
        return redirect("login")


def profile_edit(request, para):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            name = request.POST['name']
            # email = request.POST['email']
            mobile = request.POST['mobile']
            if 'profile_img' in request.FILES:
                profile_img = request.FILES['profile_img']
            if 'profile_image_check' in request.POST:
                profile_image_check = request.POST['profile_image_check']
            gender = request.POST['gender']
            dob = request.POST['dob']
            # city = request.POST['city']
            # country = request.POST['country']
            lat = request.POST['lat']
            long = request.POST['long']
            snap = request.POST['snap']
            fb = request.POST['fb']
            insta = request.POST['insta']
            website = request.POST['website']
            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
            if 'avatar_check' in request.POST:
                avatar_check = request.POST['avatar_check']
            if 'bitmoji' in request.FILES:
                bitmoji = request.FILES['bitmoji']
            if 'bitmoji_check' in request.POST:
                bitmoji_check = request.POST['bitmoji_check']
           
        #   Getting City and country based on latitude and longitude
            url ="https://api.mapbox.com/geocoding/v5/mapbox.places/"+lat+","+long+".json?types=poi&access_token=pk.eyJ1IjoiYXJhYmFwcCIsImEiOiJjbDh2YmtiODQwNXo4M29udTA0eWxldmIxIn0.tzc8bwS-5vvdE32_T0EY7A" 
            resp = requests.get(url) 
            data = json.loads(resp.content.decode()) 
            for i,j in data.items():
                if i=="features": 
                    for k in j: 
                        print(k)
                        country=k['context'][-1]['text']
                        state=k['context'][-2]['text']
                        city=k['context'][-3]['text']

            obj = Profile.objects.get(username=int(username))
            obj.name = name
            # obj.email = email
            obj.mobile = mobile
            if 'profile_image_check' in request.POST:
                if profile_image_check:
                    obj.profile_image = None
            if 'profile_img' in request.FILES:
                if profile_img != "":
                    obj.profile_image = profile_img
                
            obj.gender = gender
            if dob != "None":
                obj.dob = dob
            obj.city = city
            obj.country = country
            if lat != "None":
                obj.lat = lat
            if long != "None":
                obj.long = long
            obj.snap = snap
            obj.fb = fb
            obj.insta = insta
            obj.website = website
            if 'avatar_check' in request.POST:
                if avatar_check:
                    obj.avatar = None
            if 'avatar' in request.FILES:
                if avatar != "":
                    obj.avatar = avatar
            if 'bitmoji_check' in request.POST:
                if bitmoji_check:
                    obj.bitmoji = None
            if 'bitmoji' in request.FILES:
                if bitmoji != "":
                    obj.bitmoji = bitmoji
            obj.save()

            return redirect('Profile')

        elif request.method == "GET":
            modal_id = para.split(" ")
            obj = Profile.objects.filter(uid=modal_id[1])
            data = serializers.serialize("json", obj)
            data = json.loads(data)
            res = []
            for i in data:
                res.append(i['fields'])
            return render(request, 'admin_site/profile_edit.html', {"result": res})
    else:
        return redirect("login")


def preferences_edit(request, para):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            signature = request.POST['signature']
            if 'signature_check' in request.POST:
                signature_check = request.POST['signature_check']
            export_quality = request.POST['export_quality']
            Language = request.POST['Language']
            user_stared_templates = request.POST['user_stared_templates']
            user_stared_backgrounds = request.POST['user_stared_backgrounds']
            user_stared_stickers = request.POST['user_stared_stickers']
            user_stared_Textart = request.POST['user_stared_Textart']
            user_stared_colors = request.POST['user_stared_colors']
            user_stared_fonts = request.POST['user_stared_fonts']
            most_used_fonts = request.POST['most_used_fonts']
            user_custom_colors = request.POST['user_custom_colors']
            instagram_follower = request.POST.get('instagram_follower')
            grid_snapping = request.POST.get('grid_snapping')
            user_recent_text = request.POST['user_recent_text']
            appearance_mode = request.POST['appearance_mode']
            enable_iCloud_backup = request.POST.get('enable_iCloud_backup')
            save_projects_automatically = request.POST.get(
                'save_projects_automatically')
            save_projects_on_export = request.POST.get(
                'save_projects_on_export')
            notifications_permission = request.POST.get(
                'notifications_permission')
            inApp_notifications_permission = request.POST.get(
                'inApp_notifications_permission')
            photo_library_permission = request.POST.get(
                'photo_library_permission')
            digital_riyals_rewards = request.POST['digital_riyals_rewards']
            enable_touch = request.POST.get('enable_touch')
            app_theme = request.POST['app_theme']
            always_crop = request.POST.get('always_crop')

            obj = user_preference.objects.get(username=int(username))
            if 'signature_check' in request.POST:
                if signature_check:
                    obj.signature = None
            if signature != "":
                obj.signature = signature
            obj.export_quality = export_quality
            obj.Language = Language

            if user_stared_templates != "[]":
                obj.user_stared_templates = user_stared_templates.replace(
                    "[", "{").replace("]", "}")
            if user_stared_backgrounds != "[]":
                obj.user_stared_backgrounds = user_stared_backgrounds.replace(
                    "[", "{").replace("]", "}")
            if user_stared_stickers != "[]":
                obj.user_stared_stickers = user_stared_stickers.replace(
                    "[", "{").replace("]", "}")
            if user_stared_Textart != "[]":
                obj.user_stared_Textart = user_stared_Textart.replace(
                    "[", "{").replace("]", "}")
            if user_stared_colors != "[]":
                obj.user_stared_colors = user_stared_colors.replace(
                    "[", "{").replace("]", "}")
            if user_stared_fonts != "[]":
                obj.user_stared_fonts = user_stared_fonts.replace(
                    "[", "{").replace("]", "}")
            if most_used_fonts != "[]":
                obj.most_used_fonts = most_used_fonts.replace(
                    "[", "{").replace("]", "}")
            if user_custom_colors != "[]":
                obj.user_custom_colors = user_custom_colors.replace(
                    "[", "{").replace("]", "}")

            if instagram_follower == "on":
                obj.instagram_follower = True
            else:
                obj.instagram_follower = False

            if grid_snapping == "on":
                obj.grid_snapping = True
            else:
                obj.grid_snapping = False

            obj.user_recent_text = user_recent_text
            obj.appearance_mode = appearance_mode

            if enable_iCloud_backup == "on":
                obj.enable_iCloud_backup = True
            else:
                obj.enable_iCloud_backup = False

            if save_projects_automatically == "on":
                obj.save_projects_automatically = True
            else:
                obj.save_projects_automatically = False

            if save_projects_on_export == "on":
                obj.save_projects_on_export = True
            else:
                obj.save_projects_on_export = False

            if notifications_permission == "on":
                obj.notifications_permission = True
            else:
                obj.notifications_permission = False

            if inApp_notifications_permission == "on":
                obj.inApp_notifications_permission = True
            else:
                obj.inApp_notifications_permission = False

            if photo_library_permission == "on":
                obj.photo_library_permission = True
            else:
                obj.photo_library_permission = False

            obj.digital_riyals_rewards = digital_riyals_rewards

            if enable_touch == "on":
                obj.enable_touch = True
            else:
                obj.enable_touch = False

            obj.app_theme = app_theme

            if always_crop == "on":
                obj.always_crop = True
            else:
                obj.always_crop = False

            obj.save()

            return redirect('user_preference')

        elif request.method == "GET":
            modal_id = para.split(" ")
            obj = user_preference.objects.filter(udid=modal_id[1])
            data = serializers.serialize("json", obj)
            data = json.loads(data)
            res = []
            for i in data:
                res.append(i['fields'])
            return render(request, 'admin_site/preferences_edit.html', {"result": res})
    else:
        return redirect("login")


def app_data_edit(request, para):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            UID = request.POST['UID']
            inApp_Products = request.POST['inApp_Products']
            Purchase_date = request.POST['Purchase_date']
            # Purchase_date_change = request.POST['Purchase_date_change']
            Purchased_product = request.POST['Purchased_product']
            Device_Model = request.POST['Device_Model']
            operating_system = request.POST['operating_system']
            Device_Storage = request.POST['Device_Storage']
            Lunch_count = request.POST['Lunch_count']
            Push_Notification_Status = request.POST.get('Push_Notification_Status')
            Library_permission_Status = request.POST.get(
                'Library_permission_Status')
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            Carrier = request.POST['Carrier']
            App_Last_Opened = request.POST.get('App_Last_Opened')
            # App_Last_Opened_change = request.POST['App_Last_Opened_change']
            Purchase_attempts = request.POST['Purchase_attempts']
            Grace_Period = request.POST['Grace_Period']
            Remaining_grace_period_days = request.POST['Remaining_grace_period_days']
            Number_of_projects = request.POST['Number_of_projects']
            Total_time_spent = request.POST['Total_time_spent']
            total_ads_served = request.POST['total_ads_served']
            Registered_user = request.POST['Registered_user']
            Push_Notification_token = request.POST['Push_Notification_token']

            obj = application_data.objects.get(username=int(username))
            obj.UID = UID
            obj.inApp_Products = inApp_Products

            if Purchase_date != "None":
                obj.Purchase_date = Purchase_date
            # obj.Purchase_date_change = Purchase_date_change
            obj.Purchased_product = Purchased_product
            obj.Device_Model = Device_Model
            obj.operating_system = operating_system
            obj.Device_Storage = Device_Storage
            obj.Lunch_count = Lunch_count

            if Push_Notification_Status == "on":
                obj.Push_Notification_Status = True
            else:
                obj.Push_Notification_Status = False

            if Library_permission_Status == "on":
                obj.Library_permission_Status = True
            else:
                obj.Library_permission_Status = False

            if latitude != "":
                obj.latitude = latitude
            if longitude != "":
                obj.longitude = longitude
            obj.Carrier = Carrier
            if App_Last_Opened != "None":
                obj.App_Last_Opened = App_Last_Opened
            # obj.App_Last_Opened_change = App_Last_Opened_change
            obj.Purchase_attempts = Purchase_attempts
            obj.Grace_Period = Grace_Period
            obj.Remaining_grace_period_days = Remaining_grace_period_days
            obj.Number_of_projects = Number_of_projects
            obj.Total_time_spent = Total_time_spent
            obj.total_ads_served = total_ads_served

            if Registered_user == "on":
                obj.Registered_user = True
            else:
                obj.Registered_user = False

            obj.Push_Notification_token = Push_Notification_token

            obj.save()

            return redirect('application_data')

        elif request.method == "GET":
            modal_id = para.split(" ")
            obj = application_data.objects.filter(aid=modal_id[1])
            data = serializers.serialize("json", obj)
            data = json.loads(data)
            res = []
            for i in data:
                res.append(i['fields'])
            return render(request, 'admin_site/app_data_edit.html', {"result": res})
    else:
        return redirect("login")


def no_auth_app_data_edit(request, para):
   
    if request.user.is_authenticated:
        if request.method == "POST":
            
            UID = request.POST['UID']
            inApp_Products = request.POST['inApp_Products']
            Purchase_date = request.POST['Purchase_date']
            print("===>",Purchase_date)
            # Purchase_date_change = request.POST['Purchase_date_change']
            Purchased_product = request.POST['Purchased_product']
            Device_Model = request.POST['Device_Model']
            operating_system = request.POST['operating_system']
            Device_Storage = request.POST['Device_Storage']
            Lunch_count = request.POST['Lunch_count']
            Push_Notification_Status = request.POST.get('Push_Notification_Status')
            Library_permission_Status = request.POST.get(
                'Library_permission_Status')
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            Carrier = request.POST['Carrier']
            App_Last_Opened = request.POST.get('App_Last_Opened')
            # App_Last_Opened_change = request.POST['App_Last_Opened_change']
            Purchase_attempts = request.POST.get('Purchase_attempts')
            print("<===",Lunch_count,"===>")
            Grace_Period = request.POST['Grace_Period']
            Remaining_grace_period_days = request.POST['Remaining_grace_period_days']
            Number_of_projects = request.POST['Number_of_projects']
            Total_time_spent = request.POST['Total_time_spent']
            total_ads_served = request.POST['total_ads_served']
            Registered_user = request.POST.get('Registered_user')
            Push_Notification_token = request.POST['Push_Notification_token']

            if Purchase_attempts != "":
                Purchase_attempts = Purchase_attempts
            else:
                Purchase_attempts = None

            if Lunch_count != '':
                Lunch_count = Lunch_count
            else:
                Lunch_count = None

            if Number_of_projects != '':
                Number_of_projects = Number_of_projects
            else:
                Number_of_projects = None

            if total_ads_served != '':
                total_ads_served = total_ads_served
            else:
                total_ads_served = None

            if Remaining_grace_period_days != '':
                Remaining_grace_period_days = Remaining_grace_period_days
            else:
                Remaining_grace_period_days = None

            obj = application_data_noauth.objects.get(UID=UID)
            obj.inApp_Products = inApp_Products

            obj.Purchase_attempts = Purchase_attempts

            if Purchase_date != "None":
                obj.Purchase_date = Purchase_date
            # obj.Purchase_date_change = Purchase_date_change
            obj.Purchased_product = Purchased_product
            obj.Device_Model = Device_Model
            obj.operating_system = operating_system
            obj.Device_Storage = Device_Storage
            obj.Lunch_count = Lunch_count

            if Push_Notification_Status == "on":
                obj.Push_Notification_Status = True
            else:
                obj.Push_Notification_Status = False

            if Library_permission_Status == "on":
                obj.Library_permission_Status = True
            else:
                obj.Library_permission_Status = False

            if latitude != "":
                obj.latitude = latitude
            if longitude != "":
                obj.longitude = longitude
            obj.Carrier = Carrier
            if App_Last_Opened != "None":
                obj.App_Last_Opened = App_Last_Opened
            # obj.App_Last_Opened_change = App_Last_Opened_change
            obj.Grace_Period = Grace_Period
            obj.Remaining_grace_period_days = Remaining_grace_period_days
            obj.Number_of_projects = Number_of_projects
            obj.Total_time_spent = Total_time_spent
            obj.total_ads_served = total_ads_served

            if Registered_user == "on":
                obj.Registered_user = True
            else:
                obj.Registered_user = False

            obj.Push_Notification_token = Push_Notification_token

            obj.save()

            return redirect('no_auth_app_data_model')

        elif request.method == "GET":
            modal_id = para.split(" ")
            obj = application_data_noauth.objects.filter(aid=modal_id[1])
            data = serializers.serialize("json", obj)
            data = json.loads(data)
            res = []
            for i in data:
                res.append(i['fields'])
            return render(request, 'admin_site/no_auth_app_data_edit.html', {"result": res})
    else:
        return redirect("login")


def purchase_edit(request, para):
    
    if request.user.is_authenticated:
        if request.method == "POST":
            pk = request.POST['username']
            pstatus = request.POST['pstatus']
            auto_renew_status = request.POST.get('auto_renew_status')
            is_in_billing_retry_period = request.POST.get(
                'is_in_billing_retry_period')
            is_in_intro_offer_period = request.POST.get(
                'is_in_intro_offer_period')
            is_trial_period = request.POST.get('is_trial_period')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            subscription_type = request.POST.get('subscription_type')
            
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                messages.error(request, 'Start date in incorrect date format. It should be YYYY-MM-DD.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                messages.error(request, 'End date in incorrect date format. It should be YYYY-MM-DD.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            obj = Purchase.objects.get(purchase_id=para.split(" ")[1])
            
            obj.pstatus = pstatus
            if auto_renew_status == "on":
                obj.auto_renew_status = True
            else:
                obj.auto_renew_status = False

            if is_in_billing_retry_period == "on":
                obj.is_in_billing_retry_period = True
            else:
                obj.is_in_billing_retry_period = False

            if is_in_intro_offer_period == "on":
                obj.is_in_intro_offer_period = True
            else:
                obj.is_in_intro_offer_period = False

            if is_trial_period == "on":
                obj.is_trial_period = True
            else:
                obj.is_trial_period = False

            if start_date != str(None):
                obj.start_date = start_date
            if end_date != str(None):
                obj.end_date = end_date
            obj.subscription_type = subscription_type
            obj.start_date = start_date
            obj.end_date = end_date
            obj.subscription_type = subscription_type
            obj.save()

            return redirect('Purchase')

        elif request.method == "GET":
            modal_id = para.split(" ")
            obj = Purchase.objects.filter(purchase_id=modal_id[1])
            data = serializers.serialize("json", obj)
            data = json.loads(data)
            return render(request, 'admin_site/purchase_edit.html', {"result": data})
    else:
        return redirect("login")


def tag_edit(request, para):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            tag = request.POST['tag']

            obj = Tag.objects.get(username=username)
            obj.tag = tag.replace("[", "{").replace("]", "}")
            obj.save()

            return redirect('Tag')

        elif request.method == "GET":
            modal_id = para.split(" ")
            obj = Tag.objects.filter(id=modal_id[1])
            data = serializers.serialize("json", obj)
            data = json.loads(data)
            res = []
            for i in data:
                res.append(i['fields'])
            return render(request, 'admin_site/tag_edit.html', {"result": res})
    else:
        return redirect("login")


def product_edit(request, para):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            productID = request.POST['productID']
            product = request.POST['product']
            productPromo = request.POST['productPromo']
            promoPrice = request.POST.get('promoPrice')
            annaulSubProd = request.POST['annaulSubProd']
            annaulSub = request.POST['annaulSub']
            monthlySubProd = request.POST['monthlySubProd']
            monthlySub = request.POST['monthlySub']
            localeId = request.POST['localeId']

            obj = Product.objects.get(username=username)
            obj.productID = productID
            obj.product = product
            obj.productPromo = productPromo
            if promoPrice != "":
                obj.promoPrice = promoPrice
            obj.annaulSubProd = annaulSubProd
            obj.annaulSub = annaulSub
            obj.monthlySubProd = monthlySubProd
            obj.monthlySub = monthlySub
            if localeId != "":
                obj.localeId = localeId
            obj.save()

            return redirect('Product')

        elif request.method == "GET":
            modal_id = para.split(" ")
            obj = Product.objects.filter(PID=modal_id[1])
            data = serializers.serialize("json", obj)
            data = json.loads(data)
            res = []
            for i in data:
                res.append(i['fields'])
            return render(request, 'admin_site/product_edit.html', {"result": res})
    else:
        return redirect("login")

def change_password(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            old_password = request.POST['old_password']
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']
            if request.user.check_password(old_password):
                if new_password == confirm_password:
                    pat = re.compile(reg)
                    mat = re.search(pat, new_password)
                    if mat:
                        request.user.set_password(new_password)
                        request.user.save()
                        messages.success(
                            request, 'Password changed successfully.')
                        return redirect('index')
                    else:
                        messages.error(
                            request, 'password must be include atleast one special character,number,small and capital letter and length between 6 to 20!!!')
                else:
                    messages.error(
                        request, "New Password and Confirm password doesn't matched!!!")
            else:
                messages.error(request, 'Please check your old password!')
        return render(request, 'admin_site/change_password.html')
    else:
        return redirect("login")

# edit specific model data end---------/

# send mail for forgot password
def send_link(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            obj = custom_user.objects.get(email=email)
            # Link = 'http://127.0.0.1:8001/admin-site/forgot_password/'
            Link = 'https://kitaba.me/admin-site/forgot_password/'
            characters = string.ascii_letters + string.digits + punctuation
            token = ''.join(random.choice(characters) for i in range(50))
            encrypted_token = base64.b64encode(
                token.encode("ascii")).decode("ascii")
            
            obj.confirm_token = token
            obj.save()

            subject = 'Forgot Password'
            html_message = render_to_string(
                'mail_template.html', {'token': f'{Link}{encrypted_token}'})
            plain_message = strip_tags(html_message)
            from_email = 'From <no-reply@3rabapp.com>'
            to = email
            
            mail.send_mail(subject, plain_message, from_email,
                           [to], html_message=html_message)
            messages.success(request, "Please check your email box")
        except Exception as e:
            messages.error(
                request, "Entered email is not matched with any user!!!")
    return render(request, 'admin_site/forgot_password.html')

# for forgot password
def forgot_password(request,token):
    if request.method == "POST":
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        decrypted_token = base64.b64decode(token).decode("ascii")
        
        try:
            obj = custom_user.objects.get(confirm_token = decrypted_token)
            pat = re.compile(reg)
            mat = re.search(pat, new_password)
            if mat:
                if new_password == confirm_password:
                    obj.set_password(new_password)
                    obj.save()
                    messages.success(request, "Password updated successfully.")
                    return redirect('index')
                else:
                    messages.error(request, "new password and confirm password doesnot matched!!!")
            else:
                messages.error(request, "password must be include atleast one special character,number,small and capital letter and length between 6 to 20!")
        except:
            messages.error(request, "Check your link!!!")
    return render(request,'admin_site/reset.html')

# logout
def logoutprocess(request):
    logout(request)
    return redirect("login")

def filter(request):
    if request.user.is_authenticated:
        countries = Profile.objects.values('country').distinct()
        country_list1 = []
        for i in countries:
            
            if i != 'None' or i !='none':
                country_list1.append(str(i['country']).upper())
        country_list1 = set(country_list1)
        country_list = []
        for i in country_list1:
            if i=='NONE':
                pass
            else:
                country_list.append(i)

        cities = Profile.objects.values('city').distinct()
        city_list1 = []
        for i in cities:
            if i != 'None' or i !='none':
                city_list1.append(str(i['city']).upper())
        city_list1 = set(city_list1)
        city_list = []
        for i in city_list1:
            if i=='NONE':
                pass
            else:
                city_list.append(i)

        total_profiles = Profile.objects.all().order_by('-created_at')

        first_record = total_profiles[0].created_at
        last_record = total_profiles.reverse()[0].created_at
        first_record = first_record.strftime("%Y-%m-%d")
        last_record = last_record.strftime("%Y-%m-%d")

        smallest_age_record = ""
        biggest_age_record = ""
        filter_mobile_val = ""
        latitude = ""
        longitude = ""

        if 'search' in request.GET:
            searchvalue = request.GET['search']
            total_profiles = Profile.objects.filter(
                                Q(name__icontains=searchvalue) |
                                Q(mobile__icontains=searchvalue) |
                                Q(gender__icontains=searchvalue) |
                                Q(city__icontains=searchvalue) |
                                Q(country__icontains=searchvalue)
                            )

        if 'filter_mobile' in request.GET:
            searchvalue = request.GET['filter_mobile']
            filter_mobile_val = searchvalue
            total_profiles = Profile.objects.filter(Q(mobile__icontains=searchvalue))

        if 'gender' in request.GET:
            val = request.GET['gender']
            if val == 'All':
                total_profiles = total_profiles.all()
            if val == 'Male':
                total_profiles = total_profiles.filter(gender__iexact="Male")
            if val == 'Female':
                total_profiles = total_profiles.filter(gender__iexact="Female")
            if val == 'Other':
                total_profiles = total_profiles.filter(gender__iexact="Other")

        if 'age' in request.GET:
            val = request.GET['age']
            if val == 'All':
                total_profiles = total_profiles.all()
            if val == 'twenty':
                total_profiles = total_profiles.filter(dob__gte=datetime.now(
                ) - timedelta(days=(365*30)), dob__lt=datetime.now() - timedelta(days=(365*20)))
            if val == 'thirty':
                total_profiles = total_profiles.filter(dob__gte=datetime.now(
                ) - timedelta(days=(365*40)), dob__lt=datetime.now() - timedelta(days=(365*30)))
            if val == 'greater':
                total_profiles = total_profiles.filter(
                    dob__lte=datetime.now() - timedelta(days=(365*40)))

        if 'city' in request.GET:
            val = request.GET['city']
            print("CITY")
            print(val)

            if val == 'All':
                total_profiles = total_profiles.all()
            for i in city_list:
                if i == val:
                    total_profiles = total_profiles.filter(city__iexact=val)

        if 'country' in request.GET:
            val = request.GET['country']
            if val == 'All':
                total_profiles = total_profiles.all()
            for i in country_list:
                if i == val:
                    total_profiles = total_profiles.filter(country__iexact=val)                  

        if 'password_update' in request.GET:
            val = request.GET['password_update']
            if val == 'All':
                total_profiles = total_profiles.all()
            if val == 'today':
              total_profiles = total_profiles.filter(
                    pass_update__exact=datetime.now())
            if val == 'seven':
                total_profiles = total_profiles.filter(pass_update__gte=datetime.now(
                ) - timedelta(days=7), pass_update__lte=datetime.now())
            if val == 'month':
                total_profiles = total_profiles.filter(pass_update__gte=datetime.now(
                ) - timedelta(days=30), pass_update__lte=datetime.now())
            if val == 'year':
                total_profiles = total_profiles.filter(pass_update__gte=datetime.now(
                ) - timedelta(days=365), pass_update__lte=datetime.now())


        if 'fromtodate' in request.GET:
            print("fromtodate")
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']

            format_data = "%Y-%m-%d %H:%M:%S"
            start_date = datetime.strptime(start_date+" 00:00:00", format_data)
            end_date = datetime.strptime(end_date+" 23:59:59", format_data)

            total_profiles = total_profiles.filter(created_at__gte = start_date, created_at__lte = end_date)

            last_record = start_date.strftime("%Y-%m-%d")
            first_record = end_date.strftime("%Y-%m-%d")

        if 'agefilter' in request.GET:
            start_age = request.GET['start_age']
            end_age = request.GET['end_age']

            if not start_age:
                start_age = 0

            if len(end_age) == 0:
                total_profiles = total_profiles.filter(dob__lt=datetime.now() - timedelta(days=(365*int(start_age))))
            else:
                total_profiles = total_profiles.filter(dob__gte=datetime.now(
                    ) - timedelta(days=(365*int(end_age))), dob__lt=datetime.now() - timedelta(days=(365*int(start_age))))

            smallest_age_record = start_age
            biggest_age_record = end_age

        if 'radius' in request.GET:
            latitude = request.GET['latitude']
            longitude = request.GET['longitude']
            total_profiles = total_profiles.filter(Q(lat__icontains = latitude) |  Q(long__icontains = longitude))

        if 'show' in request.GET:
            showval = request.GET['show']
            p = Paginator(total_profiles, showval)
        else:
            p = Paginator(total_profiles, 10)
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)

        print(page_obj, type(page_obj))
        for i in page_obj:
            print(i)
        # from django.http import JsonResponse
        from django.core import serializers
        return HttpResponse(serializers.serialize(queryset = page_obj, format="json"))
        # return JsonResponse({"total_profiles": page_obj})

        # return render(request, "admin_site/profile_model.html", {'total_profiles': page_obj, 'total_records':len(page_obj), 'country_list':country_list, 'city_list':city_list, "first_record": first_record, "last_record": last_record, "smallest_age_record":smallest_age_record, "biggest_age_record":biggest_age_record, "filter_mobile_val":filter_mobile_val, "searched_lat":latitude, "searched_long":longitude})
    else:
        return redirect("login")