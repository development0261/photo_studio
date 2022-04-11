
import json
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.http import JsonResponse
from NewProject.settings import TIME_ZONE
from .models import custom_user
from .models import Profile, user_preference, application_data, Purchase, Product
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import UserSerializer, UserSerializerWithToken, RegistrationSerializer, SocialSerializer, ProfileSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.core.mail import send_mail
import random
import string
import re
from datetime import datetime, timezone, timedelta
from rest_framework import status
import base64
from django.contrib.auth.hashers import check_password

custom_user = get_user_model()
reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#$%&*+,-./:;<=>?@\^_`|~])[A-Za-z\d!#$%&*+,-./:;<=>?@\^_`|~]{6,20}$"
for_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
punctuation = "!#$%&()*+, -./:;<=>?@[\]^_`{|}~"

users_obj = custom_user.objects.filter(is_active=False)
for row in users_obj:
    if row.delete_date + timedelta(days=30):
        users_obj.delete()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        if custom_user.objects.filter(username=attrs['username']).exists():
            if not check_password(attrs['password'], custom_user.objects.get(username=attrs['username']).password):
                return {"Error": "Invalid Password"}
            else:
                data = super().validate(attrs)
                serializer = UserSerializerWithToken(self.user).data
                for k, v in serializer.items():
                    data[k] = v
                from django.contrib.auth.models import update_last_login
                user_obj = authenticate(username=attrs['username'], password=attrs['password'])
                update_last_login(None, user_obj)
                return data
        else:
            return {"Error": "Account with this username is not exists"}


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logoutProcess(request):
    logout(request)
    return Response({"Message": "Successfully Logged Out"}, status=status.HTTP_200_OK)

# import pandas as pd
# file_name = 'media/test_ali.xlsx'
# dfs = pd.read_excel(file_name, sheet_name=None)
# print(dfs)
# print('start')
# rows = []
# with open(file_name, "r", encoding="unicode_escape") as f:
#     for line in f:
#         rows.append(line.split(","))
# print(rows)
# for row in dfs:
#     for i in dfs[row]:
#         print(i)
#         print("--------!")

@api_view(['POST'])
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        print(username)
        email = request.POST['email']
        print(email)
        password = request.POST['password']
        print(password)
        name = request.POST['name']
        print(name)
        mobile = request.POST['mobile']
        print(mobile)
        gender = request.POST['gender']
        print(gender)

        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']

        if not custom_user.objects.filter(username=username).exists():
            if len(username) > 5:
                if not custom_user.objects.filter(email=email).exists():
                    if len(mobile) > 0:
                        if not Profile.objects.filter(mobile=mobile).exists() and len(mobile) > 0:
                            if(re.fullmatch(for_email, email)):
                                pat = re.compile(reg)
                                mat = re.search(pat, password)
                                if mat:
                                    user = custom_user.objects.create_user(
                                        username=username, password=password.encode().decode("ISO-8859-1"), email=email)
                                    user.save()
                                    data = Profile(
                                        username=user, name=name, mobile=mobile, gender=gender)
                                    if 'profile_image' in request.FILES:
                                        data.profile_image = profile_image
                                    data.save()
                                    temp_obj = custom_user.objects.get(username=username)
                                    pro_obj = Profile.objects.get(username=temp_obj)
                                    if pro_obj.profile_image:
                                        img = pro_obj.profile_image
                                    else:
                                        img = ""
                                    if pro_obj.avatar:
                                        img1 = pro_obj.avatar
                                    else:
                                        img1 = ""
                                    if pro_obj.bitmoji:
                                        img2 = pro_obj.bitmoji
                                    else:
                                        img2 = ""
                                    Data = {
                                        "user": {
                                            "email": temp_obj.email,
                                            "username": temp_obj.username,
                                            "password": temp_obj.password,
                                        },
                                        "name": pro_obj.name,
                                        "email": pro_obj.email,
                                        "mobile": pro_obj.mobile,
                                        "gender": pro_obj.gender,
                                        "profile_image": img,
                                        "pass_update": pro_obj.pass_update,
                                        "pass_forgot": pro_obj.pass_forgot,
                                        "updated_at": pro_obj.updated_at,
                                        "dob": pro_obj.dob,
                                        "city": pro_obj.city,
                                        "country": pro_obj.country,
                                        "lat": pro_obj.lat,
                                        "long": pro_obj.long,
                                        "snap": pro_obj.snap,
                                        "fb": pro_obj.fb,
                                        "insta": pro_obj.insta,
                                        "website": pro_obj.website,
                                        "avatar": img1,
                                        "bitmoji": img2,
                                        # "username": pro_obj.username,
                                    }
                                    return Response({"data":Data}, status=status.HTTP_200_OK)
                                else:
                                    return Response({"Error": "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({"Error": "Enter valid email address"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"Error": "Phone number already registered"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if(re.fullmatch(for_email, email)):
                            pat = re.compile(reg)
                            mat = re.search(pat, password)
                            if mat:
                                user = custom_user.objects.create_user(
                                    username=username, password=password, email=email)
                                user.save()
                                data = Profile(
                                    username=user, name=name, mobile=mobile, gender=gender)
                                if 'profile_image' in request.FILES:
                                    data.profile_image = profile_image
                                data.save()
                                temp_obj = custom_user.objects.get(username=username)
                                pro_obj = Profile.objects.get(username=temp_obj)
                                if pro_obj.profile_image:
                                    img = pro_obj.profile_image
                                else:
                                    img = ""
                                if pro_obj.avatar:
                                    img1 = pro_obj.avatar
                                else:
                                    img1 = ""
                                if pro_obj.bitmoji:
                                    img2 = pro_obj.bitmoji
                                else:
                                    img2 = ""
                                # Data = {
                                #     "user": {
                                #         "email": temp_obj.email,
                                #         "username": temp_obj.username,
                                #         "password": temp_obj.password,
                                #     },
                                #     "name": pro_obj.name,
                                #     "email": pro_obj.email,
                                #     "mobile": pro_obj.mobile,
                                #     "gender": pro_obj.gender,
                                #     "profile_image": img,
                                #     "pass_update": pro_obj.pass_update,
                                #     "pass_forgot": pro_obj.pass_forgot,
                                #     "updated_at": pro_obj.updated_at,
                                #     "dob": pro_obj.dob,
                                #     "city": pro_obj.city,
                                #     "country": pro_obj.country,
                                #     "lat": pro_obj.lat,
                                #     "long": pro_obj.long,
                                #     "snap": pro_obj.snap,
                                #     "fb": pro_obj.fb,
                                #     "insta": pro_obj.insta,
                                #     "website": pro_obj.website,
                                #     "avatar": img1,
                                #     "bitmoji": img2,
                                #     # "username": pro_obj.username,
                                # }
                                temp_obj = custom_user.objects.get(username=username)
                                serializer_class = RegistrationSerializer(pro_obj)
                                return Response({"Data": serializer_class.data}, status=status.HTTP_200_OK)
                                # return Response({"data":Data}, status=status.HTTP_200_OK)
                            else:
                                return Response({"Error": "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"Error": "Enter valid email address"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"Error": "User Already Exist with this email address"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Error": "Username length must be greater than 6"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # temp_obj = custom_user.objects.get(username=username)
            # serializer_class = RegistrationSerializer(temp_obj)
            # return Response({"Data": serializer_class.data}, status=status.HTTP_200_OK)
            return Response({"Error": "User Already Exists!!!"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def social_media_registration(request):
    if request.method == "POST":
        social_token = request.POST['social_token']
        social_registration = request.POST['social_registration']
        social_account = request.POST['social_account']

        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']

        if 'username' in request.POST:
            username = request.FILES['username']
        else:
            username = social_token

        if 'email' in request.POST:
            email = request.FILES['email']
        else:
            email = social_account

        if social_token:
            if not custom_user.objects.filter(social_token=social_token).exists():
                user = custom_user.objects.create_user(
                    username=username[0:10], password=social_token, email=email,
                    social_token=social_token, social_registration=social_registration, social_account=social_account)
                user.save()

                data = Profile(username=user)
                if 'profile_image' in request.FILES:
                    data.profile_image = profile_image
                data.save()

                user_obj = custom_user.objects.get(social_token=social_token)
                profile_obj = Profile.objects.get(username=user_obj.id)
                serializer_class = SocialSerializer(profile_obj)
                return Response({"Data":serializer_class.data}, status=status.HTTP_200_OK)
            else:
                user_obj = custom_user.objects.get(social_token=social_token)
                profile_obj = Profile.objects.get(username=user_obj.id)
                serializer_class = SocialSerializer(profile_obj)
                return Response({"Data":serializer_class.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def send_link(request):
    if request.method == "POST":
        email = request.POST['email']
        recipient_list = []
        if custom_user.objects.filter(email=email).exists():
            user_with_email = custom_user.objects.get(email=email)
            recipient_list.append(user_with_email.email)

            # Link = 'http://127.0.0.1:8001/home/forgot_password/'
            Link = 'http://185.146.21.235:7800/home/forgot_password/'
            characters = string.ascii_letters + string.digits + punctuation
            token = ''.join(random.choice(characters) for i in range(50))
            encrypted_token = base64.b64encode(
                token.encode("ascii")).decode("ascii")
            user = custom_user.objects.get(email=email)
            user.confirm_token = token
            user.save()

            from django.core import mail
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags

            subject = 'Forgot Password'
            html_message = render_to_string(
                'mail_template.html', {'token': f'{Link}{encrypted_token}'})
            plain_message = strip_tags(html_message)
            from_email = 'From <demo.logixbuiltinfo@gmail.com>'
            to = recipient_list[0]

            mail.send_mail(subject, plain_message, from_email,
                           [to], html_message=html_message)
            return Response({"Success": "Check Your email for Forgot Password"}, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "custom_user Not Exist with this email address"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def forgot_password(request, t):
    if request.method == "POST":
        decrypted_token = base64.b64decode(t).decode("ascii")
        email = request.POST['email']
        new_pass = request.POST['new_pass']
        confirm_pass = request.POST['confirm_pass']

        if custom_user.objects.filter(email=email).exists():
            if custom_user.objects.filter(confirm_token=decrypted_token).exists():
                reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#$%&*+,-./:;<=>?@\^_`|~])[A-Za-z\d!#$%&*+,-./:;<=>?@\^_`|~]{6,20}$"
                pat = re.compile(reg)
                mat = re.search(pat, new_pass)
                if mat:
                    if new_pass == confirm_pass:
                        obj1 = custom_user.objects.get(
                            confirm_token=decrypted_token)
                        obj1.set_password(new_pass)
                        obj2 = custom_user.objects.get(
                            confirm_token=decrypted_token).profile
                        obj2.pass_forgot = datetime.now()
                        obj1.save()
                        obj2.save()
                        return Response({"Success": "password updated Successfully."}, status=status.HTTP_200_OK)
                    else:
                        return Response({"Error": "new password and confirm password doesnot matched."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"Error": "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Error": "Oops!! Please check your Token"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"Error": "custom_user Not Exist with this email address"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        new_pass = request.POST['new_pass']
        confirm_pass = request.POST['confirm_pass']
        if custom_user.objects.filter(username=username).exists():
            user = authenticate(username=username, password=password)
            if user:
                pat = re.compile(reg)
                mat = re.search(pat, new_pass)
                if mat:
                    if new_pass == confirm_pass:
                        obj1 = custom_user.objects.get(username=username)
                        obj1.set_password(new_pass)
                        obj2 = custom_user.objects.get(
                            username=username).profile
                        obj2.pass_update = datetime.now()
                        obj1.save()
                        obj2.save()
                        return Response({"Success": "password updated Successfully."}, status=status.HTTP_200_OK)
                    else:
                        return Response({"Error": "new password and confirm password doesnot matched."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"Error": "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Error": "username and password doesnot matched."}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"Error": "custom_user Not Exist with this username"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def profile(request, para=None):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        mobile = request.POST['mobile']
        gender = request.POST['gender']
        # profile_image = request.FILES['profile_image']
        date_of_Birth = request.POST['dob']
        city = request.POST['city']
        country = request.POST['country']
        user_Latitude = request.POST['lat']
        user_Longitude = request.POST['long']
        snapchat = request.POST['snap']
        facebook = request.POST['fb']
        instagram = request.POST['insta']
        website = request.POST['website']
        # avatar_image = request.FILES['avatar']
        # bitmoji = request.FILES['bitmoji']

        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']
        else:
            profile_image = None

        if 'avatar_image' in request.FILES:
            avatar_image = request.FILES['avatar_image']
        else:
            avatar_image = None

        if 'bitmoji' in request.FILES:
            bitmoji = request.FILES['bitmoji']
        else:
            bitmoji = None

        user1 = authenticate(username=username, password=password)
        if user1:
            user = custom_user.objects.get(username=username).profile
            user.name = name
            user.email = email
            user.mobile = mobile
            user.gender = gender
            user.profile_image = profile_image
            if date_of_Birth != "":
                user.dob = date_of_Birth
            user.city = city
            user.country = country
            if user_Latitude != "":
                user.lat = user_Latitude
            if user_Longitude != "":
                user.long = user_Longitude
            user.snap = snapchat
            user.fb = facebook
            user.insta = instagram
            user.website = website
            user.avatar = avatar_image
            user.bitmoji = bitmoji
            user.updated_at = datetime.now()
            user.save()
            return Response({"Success": "Profile Updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "custom_user Not Exist with this username and password"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def specific_user(request):
    if request.method == "GET":
        username = request.GET['username']
        queryset = Profile.objects.filter(username__username=username)
        serializer_class = ProfileSerializer(queryset, many=True)
        return Response({'data': serializer_class.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_count(request):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer(queryset, many=True)
    return Response({'Total users': len(serializer_class.data)}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def genderwise(request):
    gen = request.GET['gender']
    print(gen)
    obj1 = Profile.objects.filter(gender=gen)
    serializer_class = ProfileSerializer(obj1, many=True)
    return Response({f'Total users with {gen} gender': len(serializer_class.data)}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def countrywise(request):
    con = request.GET['country']
    obj1 = Profile.objects.filter(country=con)
    serializer_class = ProfileSerializer(obj1, many=True)
    return Response({f'Users with {con} country': serializer_class.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def preferences(request):
    if request.method == "POST":
        username = request.POST['username']
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
        instagram_follower = request.POST['instagram_follower']
        grid_snapping = request.POST['grid_snapping']
        user_recent_text = request.POST['user_recent_text']
        appearance_mode = request.POST['appearance_mode']
        enable_iCloud_backup = request.POST['enable_iCloud_backup']
        save_projects_automatically = request.POST['save_projects_automatically']
        save_projects_on_export = request.POST['save_projects_on_export']
        notifications_permission = request.POST['notifications_permission']
        inApp_notifications_permission = request.POST['inApp_notifications_permission']
        photo_library_permission = request.POST['photo_library_permission']
        digital_riyals_rewards = request.POST['digital_riyals_rewards']
        enable_touch = request.POST['enable_touch']
        app_theme = request.POST['app_theme']
        always_crop = request.POST['always_crop']

        if 'signature' in request.FILES:
            signature = request.FILES['signature']
        else:
            signature = None

        try:
            user = custom_user.objects.get(username=username)
            try:
                if user:
                    data = user_preference(username=user,
                                    signature=signature,
                                    export_quality=export_quality,
                                    Language=Language,
                                    user_stared_templates=user_stared_templates,
                                    user_stared_backgrounds=user_stared_backgrounds,
                                    user_stared_stickers=user_stared_stickers,
                                    user_stared_Textart=user_stared_Textart,
                                    user_stared_colors=user_stared_colors,
                                    user_stared_fonts=user_stared_fonts,
                                    most_used_fonts=most_used_fonts,
                                    user_custom_colors=user_custom_colors,
                                    instagram_follower=instagram_follower,
                                    grid_snapping=grid_snapping,
                                    user_recent_text=user_recent_text,
                                    appearance_mode=appearance_mode,
                                    enable_iCloud_backup=enable_iCloud_backup,
                                    save_projects_automatically=save_projects_automatically,
                                    save_projects_on_export=save_projects_on_export,
                                    notifications_permission=notifications_permission,
                                    inApp_notifications_permission=inApp_notifications_permission,
                                    photo_library_permission=photo_library_permission,
                                    digital_riyals_rewards=digital_riyals_rewards,
                                    enable_touch=enable_touch,
                                    app_theme=app_theme,
                                    always_crop=always_crop)
                    data.save()
                    return Response({"Success": "preferences Added."}, status=status.HTTP_200_OK)
            except:
                preferences_obj = user_preference.objects.get(username=user.id)
                preferences_obj.signature = signature
                preferences_obj.export_quality = export_quality
                preferences_obj.Language = Language
                preferences_obj.user_stared_templates = user_stared_templates
                preferences_obj.user_stared_backgrounds = user_stared_backgrounds
                preferences_obj.user_stared_stickers = user_stared_stickers
                preferences_obj.user_stared_Textart = user_stared_Textart
                preferences_obj.user_stared_colors = user_stared_colors
                preferences_obj.user_stared_fonts = user_stared_fonts
                preferences_obj.most_used_fonts = most_used_fonts
                preferences_obj.user_custom_colors = user_custom_colors
                preferences_obj.instagram_follower = instagram_follower
                preferences_obj.grid_snapping = grid_snapping
                preferences_obj.user_recent_text = user_recent_text
                preferences_obj.appearance_mode = appearance_mode
                preferences_obj.enable_iCloud_backup = enable_iCloud_backup
                preferences_obj.save_projects_automatically = save_projects_automatically
                preferences_obj.save_projects_on_export = save_projects_on_export
                preferences_obj.notifications_permission = notifications_permission
                preferences_obj.inApp_notifications_permission = inApp_notifications_permission
                preferences_obj.photo_library_permission = photo_library_permission
                preferences_obj.digital_riyals_rewards = digital_riyals_rewards
                preferences_obj.enable_touch = enable_touch
                preferences_obj.app_theme = app_theme
                preferences_obj.always_crop = always_crop
                preferences_obj.save()
                return Response({"Success": "User preferences updated."}, status=status.HTTP_200_OK)
        except:
            return Response({"Error": "User not Found!!!"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def app_data(request):
    if request.method == "POST":
        username = request.POST['username']
        UID = request.POST['UID']
        inApp_Products = request.POST['inApp_Products']
        Purchase_date = request.POST['Purchase_date']
        Purchased_product = request.POST['Purchased_product']
        Device_Model = request.POST['Device_Model']
        operating_system = request.POST['operating_system']
        Device_Storage = request.POST['Device_Storage']
        Lunch_count = request.POST['Lunch_count']
        Push_Notification_Status = request.POST['Push_Notification_Status']
        Library_permission_Status = request.POST['Library_permission_Status']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
        Carrier = request.POST['Carrier']
        App_Last_Opened = request.POST['App_Last_Opened']
        Purchase_attempts = request.POST['Purchase_attempts']
        Grace_Period = request.POST['Grace_Period']
        Remaining_grace_period_days = request.POST['Remaining_grace_period_days']
        Number_of_projects = request.POST['Number_of_projects']
        Total_time_spent = request.POST['Total_time_spent']
        total_ads_served = request.POST['total_ads_served']
        Registered_user = request.POST['Registered_user']
        Push_Notification_token = request.POST['Push_Notification_token']

        user = custom_user.objects.get(username=username)
        try:
            app_data_obj = application_data.objects.get(username=user.id)
            app_data_obj.UID = UID
            app_data_obj.inApp_Products = inApp_Products
            app_data_obj.Purchase_date = Purchase_date
            app_data_obj.Purchased_product = Purchased_product
            app_data_obj.Device_Model = Device_Model
            app_data_obj.operating_system = operating_system
            app_data_obj.Device_Storage = Device_Storage
            app_data_obj.Lunch_count = Lunch_count
            app_data_obj.Push_Notification_Status = Push_Notification_Status
            app_data_obj.Library_permission_Status = Library_permission_Status
            app_data_obj.latitude = latitude
            app_data_obj.longitude = longitude
            app_data_obj.Carrier = Carrier
            app_data_obj.App_Last_Opened = App_Last_Opened
            app_data_obj.Purchase_attempts = Purchase_attempts
            app_data_obj.Grace_Period = Grace_Period
            app_data_obj.Remaining_grace_period_days = Remaining_grace_period_days
            app_data_obj.Number_of_projects = Number_of_projects
            app_data_obj.Total_time_spent = Total_time_spent
            app_data_obj.total_ads_served = total_ads_served
            app_data_obj.Registered_user = Registered_user
            app_data_obj.Push_Notification_token = Push_Notification_token
            app_data_obj.save()
            return Response({"Success": "Details Updated."}, status=status.HTTP_200_OK)
        except Exception as e:
            if user:
                try:
                    application_data.objects.get(UID=UID)
                    return Response({"Error": "UID already exists.Plese check your UID!!!"}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    data = application_data(username=user,
                                            UID=UID,
                                            inApp_Products=inApp_Products,
                                            Purchase_date=Purchase_date,
                                            Purchased_product=Purchased_product,
                                            Device_Model=Device_Model,
                                            operating_system=operating_system,
                                            Device_Storage=Device_Storage,
                                            Lunch_count=Lunch_count,
                                            Push_Notification_Status=Push_Notification_Status,
                                            Library_permission_Status=Library_permission_Status,
                                            latitude = latitude,
                                            longitude = longitude,
                                            Carrier=Carrier,
                                            App_Last_Opened=App_Last_Opened,
                                            Purchase_attempts=Purchase_attempts,
                                            Grace_Period=Grace_Period,
                                            Remaining_grace_period_days=Remaining_grace_period_days,
                                            Number_of_projects=Number_of_projects,
                                            Total_time_spent=Total_time_spent,
                                            total_ads_served=total_ads_served,
                                            Registered_user=Registered_user,
                                            Push_Notification_token=Push_Notification_token)
                    data.save()
                    return Response({"Success": "Details Added."}, status=status.HTTP_200_OK)
            else:
                return Response({"Error": "custom_user not Found!!!"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def email_verification(request):
    if request.method == "POST":
        email = request.GET['email']
        user = custom_user.objects.filter(email=email)
        if user:
            return Response({"Error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Success": "Email successfully added"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def username_verification(request):
    if request.method == "POST":
        username = request.GET['username']
        user = custom_user.objects.filter(username=username)
        if user:
            return Response({"Error": "Username already in use"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Success": "Username successfully added"}, status=status.HTTP_200_OK)


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
def purchase_history(request):
    if request.method == "POST":
        try:
            username = request.POST['username']
            pstatus = request.POST['pstatus']
            auto_renew_status = request.POST['auto_renew_status']
            is_in_billing_retry_period = request.POST['is_in_billing_retry_period']
            is_in_intro_offer_period = request.POST['is_in_intro_offer_period']
            is_trial_period = request.POST['is_trial_period']
            user = custom_user.objects.get(username=username)
            if user:
                obj = Purchase(
                    username=user,
                    pstatus=pstatus,
                    auto_renew_status=auto_renew_status,
                    is_in_billing_retry_period=is_in_billing_retry_period,
                    is_in_intro_offer_period=is_in_intro_offer_period,
                    is_trial_period=is_trial_period
                )
                obj.save()
                return Response({"Success": "Data Added"}, status=status.HTTP_200_OK)
            else:
                return Response({"Error": "custom_user Not Exist!!!"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response({"Error": "Record with same user exists"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        username = request.POST['username']
        pstatus = request.POST['pstatus']
        auto_renew_status = request.POST['auto_renew_status']
        is_in_billing_retry_period = request.POST['is_in_billing_retry_period']
        is_in_intro_offer_period = request.POST['is_in_intro_offer_period']
        is_trial_period = request.POST['is_trial_period']

        try:
            user = custom_user.objects.get(username=username)
            purchase_obj = Purchase.objects.get(username=user)
            purchase_obj.pstatus = pstatus
            purchase_obj.auto_renew_status = auto_renew_status
            purchase_obj.is_in_billing_retry_period = is_in_billing_retry_period
            purchase_obj.is_in_intro_offer_period = is_in_intro_offer_period
            purchase_obj.is_trial_period = is_trial_period
            purchase_obj.save()
            return Response({"Success": "Data Updated"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"Error": "User Not Exist!!!"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    if request.method == "POST":
        username = request.POST['username']
        try:
            user_obj = custom_user.objects.get(username=username)
            user_obj.is_active = False
            user_obj.delete_date = datetime.now()
            user_obj.save()
            return Response({"Success": "Your account is under deleting process and deleted in 30 days."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def product(request):
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

        user_obj = custom_user.objects.get(username=username)
        if user_obj:
            try:
                product1 = Product.objects.create(
                    username=user_obj,
                    productID=productID,
                    product=product,
                    productPromo=productPromo,
                    promoPrice=promoPrice,
                    annaulSubProd=annaulSubProd,
                    annaulSub=annaulSub,
                    monthlySubProd=monthlySubProd,
                    monthlySub=monthlySub,
                    localeId=localeId
                )
                return Response({"Success": "Product Details Added."}, status=status.HTTP_200_OK)

            except:
                product1 = Product.objects.filter(product=product).first()
                product1.productPromo = productPromo
                product1.promoPrice = promoPrice
                product1.annaulSubProd = annaulSubProd
                product1.annaulSub = annaulSub
                product1.monthlySubProd = monthlySubProd
                product1.monthlySub = monthlySub
                product1.localeId = localeId
                product1.save()
                return Response({"Success": "Product Details Updated."}, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "custom_user not found"}, status=status.HTTP_401_UNAUTHORIZED)
