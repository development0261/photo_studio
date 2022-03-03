from datetime import date, datetime, timedelta
import copy
from django.shortcuts import redirect, render
from home.models import Product, Profile, Purchase, Tag, application_data, custom_user, user_preference
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
# from captcha.image import ImageCaptcha
# import glob
import os
import re
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import base64
punctuation = "!#$%&()*+, -./:;<=>?@[\]^_`{|}~"
reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#$%&*+,-./:;<=>?@\^_`|~])[A-Za-z\d!#$%&*+,-./:;<=>?@\^_`|~]{6,20}$"

# Create your views here.
total_users = custom_user.objects.all()
total_profiles = Profile.objects.all()
total_details = user_preference.objects.all()
total_app_datas = application_data.objects.all()
total_purchases = Purchase.objects.all()
total_tags = Tag.objects.all()
total_products = Product.objects.all()


def loginprocess(request):
    # captcha_code = string.digits + string.ascii_lowercase + string.ascii_uppercase
    # captcha_data = ''.join(random.choice(captcha_code) for i in range(6))
    # image = ImageCaptcha(width = 280, height = 90)
    # image.write(captcha_data, 'media/CAPTCHA.png')
    # print(captcha_data)

    # list_of_files = glob.glob('D:\Photo_editor\Photo_editor\media\*') # * means all if need specific format then *.csv
    # latest_file = max(list_of_files, key=os.path.getctime)
    # latest_file = str(latest_file).split("\\")
    # latest_file = latest_file[-1]

    if 'otpSubmit' in request.POST:
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = custom_user.objects.get(email=email)
            if user.check_password(password):
                otp_gen = string.digits
                confirm_otp = ''.join(random.choice(otp_gen) for i in range(6))
                send_mail(
                    subject="OTP Verification",
                    message="Your OTP is  :  " + confirm_otp,
                    from_email='demo.logixbuiltinfo@gmail.com',
                    recipient_list=[email],
                    fail_silently=False,
                )
                user.confirm_token = confirm_otp
                user.save()
                messages.success(request, 'Check your mail Inbox.')
                return redirect('login')
                # f'/admin_site/otp-verification/{user}'
            else:
                messages.error(request, 'Please check your password!!!')
                return redirect("login")
        except Exception as e:
            print(e)
            messages.error(request, 'Please check your email!!!')
            return redirect("login")

    if 'FinalSubmit' in request.POST:
        otp = request.POST['otp']
        email = request.POST['email']
        # captcha_in = request.POST['captcha_in']
        obj = custom_user.objects.get(email=email)
        if obj.confirm_token == otp:
            # print(captcha_in, captcha_data)
            # if captcha_in == captcha_data:
            login(request, obj)
            messages.success(request, 'Login Successfully.')
            return redirect("index")
            # else:
            #     messages.error(request, 'Please check your captcha!!!')
            #     return redirect("login")
        else:
            messages.error(request, 'Please check your otp!!!')
            return redirect("login")

    return render(request, 'admin_site/login.html')


def models(request):
    app_models = apps.get_app_config('home').get_models()
    home_models = []
    for i in app_models:
        if i.__name__ == "custom_user":
            pass
        else:
            home_models.append(i.__name__)

    app_models = apps.get_app_config('otp_totp').get_models()
    totp = []
    for i in app_models:
        totp.append(i.__name__)
    return {'home_models': home_models, 'totp': totp}


def index(request):
    if request.user.is_authenticated:
        return render(request, "admin_site/index.html", {'total_users': total_users,
                                                         'total_profiles': total_profiles,
                                                         'total_details': total_details,
                                                         'total_app_datas': total_app_datas,
                                                         'total_purchases': total_purchases,
                                                         'total_tags': total_tags,
                                                         'total_products': total_products,
                                                         })
    else:
        return redirect("login")


def admin_user(request):
    if request.user.is_authenticated:
        admins = custom_user.objects.filter(is_superuser=True)
        return render(request, "admin_site/admin_user.html", {'admins': admins})
    else:
        return redirect("login")


def app_user(request):
    if request.user.is_authenticated:
        total_users = custom_user.objects.all()
        locals = custom_user.objects.filter(is_superuser=False)

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

        return render(request, "admin_site/user_model.html", {'total_users': total_users, 'locals': locals})
    else:
        return redirect("login")


def profile_model(request):
    if request.user.is_authenticated:
        total_profiles = Profile.objects.all()
        if 'filter' in request.GET:
            val = request.GET['filter']
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

            if val == 'twenty':
                total_profiles = total_profiles.filter(dob__gte=datetime.now(
                ) - timedelta(days=(365*30)), dob__lt=datetime.now() - timedelta(days=(365*20)))
            if val == 'thirty':
                total_profiles = total_profiles.filter(dob__gte=datetime.now(
                ) - timedelta(days=(365*40)), dob__lt=datetime.now() - timedelta(days=(365*30)))
            if val == 'greater':
                total_profiles = total_profiles.filter(
                    dob__lte=datetime.now() - timedelta(days=(365*40)))

            if val == 'Male':
                total_profiles = total_profiles.filter(gender="Male")
            if val == 'Female':
                total_profiles = total_profiles.filter(gender="Female")
            if val == 'Other':
                total_profiles = total_profiles.filter(gender="Other")

            if val == 'India':
                total_profiles = total_profiles.filter(country="India")
            if val == 'USA':
                total_profiles = total_profiles.filter(country="USA")

        return render(request, "admin_site/profile_model.html", {'total_profiles': total_profiles})
    else:
        return redirect("login")


def user_preference_model(request):
    if request.user.is_authenticated:
        total_details = user_preference.objects.all()
        return render(request, "admin_site/user_preferences_model.html", {'total_details': total_details})
    else:
        return redirect("login")


def app_data_model(request):
    if request.user.is_authenticated:
        total_app_datas = application_data.objects.all()
        return render(request, "admin_site/app_data_model.html", {'total_app_datas': total_app_datas})
    else:
        return redirect("login")


def purchase_model(request):
    if request.user.is_authenticated:
        total_purchases = Purchase.objects.all()
        return render(request, "admin_site/purchase_model.html", {'total_purchases': total_purchases})
    else:
        return redirect("login")


def tag_model(request):
    if request.user.is_authenticated:
        total_tags = Tag.objects.all()
        return render(request, "admin_site/tag_model.html", {'total_tags': total_tags})
    else:
        return redirect("login")


def product_model(request):
    if request.user.is_authenticated:
        total_products = Product.objects.all()
        return render(request, "admin_site/product_model.html", {'total_products': total_products})
    else:
        return redirect("login")


def view_profile(request, info):
    if request.user.is_authenticated:
        infolist = info.replace(" ", "").split('-')
        print(infolist)
        obj = Profile.objects.filter(name=infolist[2])
        data = serializers.serialize("json", obj)
        print(data)
        data = json.loads(data[1:-1])
        return JsonResponse({"res": data})
    else:
        return redirect("login")


def view_purchase(request, info):
    if request.user.is_authenticated:
        infolist = info.replace(" ", "").split('-')
        obj = Purchase.objects.filter(status=infolist[2])
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
        obj = custom_user.objects.get(username=infolist[1])
        obj = user_preference.objects.filter(username=obj.id)
        data = serializers.serialize("json", obj)
        data = json.loads(data[1:-1])
        return JsonResponse({"res": data})
    else:
        return redirect("login")


def view_product(request, info):
    if request.user.is_authenticated:
        infolist = info.replace(" ", "").split('-')
        obj = Product.objects.filter(username=infolist[1])
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


def user_edit(request, para):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            email = request.POST['email']

            obj = custom_user.objects.get(username=username)
            obj.first_name = firstname
            obj.last_name = lastname
            obj.email = email
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
            obj.first_name = firstname
            obj.last_name = lastname
            obj.email = email
            obj.save()

            return redirect('adminusers')

        elif request.method == "GET":
            modal_id = para.split(" ")
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
            print(username)
            name = request.POST['name']
            email = request.POST['email']
            mobile = request.POST['mobile']
            profile_image = request.POST['profile_image']
            gender = request.POST['gender']
            dob = request.POST['dob']
            city = request.POST['city']
            country = request.POST['country']
            lat = request.POST['lat']
            long = request.POST['long']
            snap = request.POST['snap']
            fb = request.POST['fb']
            insta = request.POST['insta']
            website = request.POST['website']
            avatar = request.POST['avatar']
            bitmoji = request.POST['bitmoji']

            obj = Profile.objects.get(username=int(username))
            obj.name = name
            obj.email = email
            obj.mobile = mobile
            if profile_image != "":
                obj.profile_image = profile_image
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
            if avatar != "":
                obj.avatar = avatar
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
            Push_Notification_Status = request.POST['Push_Notification_Status']
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


def purchase_edit(request, para):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            status = request.POST['status']
            auto_renew_status = request.POST.get('auto_renew_status')
            is_in_billing_retry_period = request.POST.get(
                'is_in_billing_retry_period')
            is_in_intro_offer_period = request.POST.get(
                'is_in_intro_offer_period')
            is_trial_period = request.POST.get('is_trial_period')
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
            subscription_type = request.POST['subscription_type']

            obj = Purchase.objects.get(username=username)
            obj.status = status
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

            obj.start_date = start_date
            obj.end_date = end_date
            obj.subscription_type = subscription_type
            obj.save()

            return redirect('Purchase')

        elif request.method == "GET":
            modal_id = para.split(" ")
            obj = Purchase.objects.filter(pid=modal_id[1])
            data = serializers.serialize("json", obj)
            data = json.loads(data)
            res = []
            for i in data:
                res.append(i['fields'])
            return render(request, 'admin_site/purchase_edit.html', {"result": res})
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
            promoPrice = request.POST['promoPrice']
            annaulSubProd = request.POST['annaulSubProd']
            annaulSub = request.POST['annaulSub']
            monthlySubProd = request.POST['monthlySubProd']
            monthlySub = request.POST['monthlySub']
            localeId = request.POST['localeId']

            obj = Product.objects.get(username=username)
            obj.productID = productID
            obj.product = product
            obj.productPromo = productPromo
            obj.promoPrice = promoPrice
            obj.annaulSubProd = annaulSubProd
            obj.annaulSub = annaulSub
            obj.monthlySubProd = monthlySubProd
            obj.monthlySub = monthlySub
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

# def filters(request, para):
#     print(para)
#     total_users = custom_user.objects.all()
#     print(total_users)

#     def get_data(n):
#         Temp = copy.copy(total_users)
#         Temp = Temp[:n]
#         set_list = custom_user.objects.filter(username__in=Temp)
#         return set_list

#     if para == 'Today':
#         print("today")
#         data = list(total_users.filter(date_joined__date=date.today()))
#         data = serializers.serialize("json", data)
#         data = json.loads(data)
#         print(data)
#         return JsonResponse({"total_users": data})

#     if para == 'Last 7 days':
#         print("last 7 days")
#         data = list(total_users.filter(date_joined__gte=datetime.now() - timedelta(days=7), date_joined__lte=datetime.now()))
#         data = serializers.serialize("json", data)
#         data = json.loads(data)
#         return JsonResponse({"total_users": data})

#     if para == 'Last 30 days':
#         print("last 30 days")
#         data = list(total_users.filter(date_joined__gte=datetime.now() - timedelta(days=30), date_joined__lte=datetime.now()))
#         data = serializers.serialize("json", data)
#         data = json.loads(data)
#         return JsonResponse({"total_users": data})

#     if para == 'Last 90 days':
#         print("last 90 days")
#         data = list(total_users.filter(date_joined__gte=datetime.now() - timedelta(days=90), date_joined__lte=datetime.now()))
#         data = serializers.serialize("json", data)
#         data = json.loads(data)
#         return JsonResponse({"total_users": data})

#     if para == 'All':
#         print("All")
#         data = serializers.serialize("json", total_users)
#         data = json.loads(data)
#         return JsonResponse({"total_users": data})

#     if para == 'Clear all filters':
#         print("Clear all filters")
#         data = serializers.serialize("json", total_users)
#         data = json.loads(data)
#         return JsonResponse({"total_users": data})

#     if para == 'Last 5':
#         return get_data(5)

#     if para == 'Last 10':
#         return get_data(10)


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


def send_link(request):
    if request.method == "POST":
        email = request.POST['email']
        print(email)
        try:
            print("try")
            obj = custom_user.objects.get(email=email)

            Link = 'http://127.0.0.1:8001/admin_site/forgot_password/'
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
            from_email = 'From <demo.logixbuiltinfo@gmail.com>'
            to = email

            mail.send_mail(subject, plain_message, from_email,
                           [to], html_message=html_message)
            messages.success(request, "Please check your email box")
        except Exception as e:
            print(e)
            messages.error(
                request, "Entered email is not matched with any user!!!")
    return render(request, 'admin_site/forgot_password.html')

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


def logoutprocess(request):
    logout(request)
    return redirect("login")
