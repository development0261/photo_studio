from django.contrib.auth import get_user_model, login, logout, authenticate
from NewProject.settings import TIME_ZONE
from .models import custom_user
from .models import Profile, user_detail, application_data, Purchase, Product
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import UserSerializer, UserSerializerWithToken, RegistrationSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.core.mail import send_mail
import random
import string
import re
from datetime import datetime, timezone, timedelta
from rest_framework import status


custom_user = get_user_model()
reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#$%&*+,-./:;<=>?@\^_`|~])[A-Za-z\d!#$%&*+,-./:;<=>?@\^_`|~]{6,20}$"
for_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

users_obj = custom_user.objects.filter(is_active=False)
for row in users_obj:
    if row.delete_date + timedelta(days=30):
        users_obj.delete()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def index(request):
    return Response({"Message": "Welcome"}, status=status.HTTP_200_OK)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data

        for k, v in serializer.items():
            data[k] = v
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logoutProcess(request):
    logout(request)
    return Response({"Message": "Successfully Logged Out"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        mobile = request.POST['mobile']
        gender = request.POST['gender']
        profile_image = request.FILES['profile_image']

        if not custom_user.objects.filter(username=username).exists():
            if len(username) > 5:
                if not custom_user.objects.filter(email=email).exists():
                    if not Profile.objects.filter(mobile=mobile).exists():
                        if(re.fullmatch(for_email, email)):
                            pat = re.compile(reg)
                            mat = re.search(pat, password)
                            if mat:
                                user = custom_user.objects.create_user(
                                    username=username, password=password, email=email)
                                user.save()
                                data = Profile(
                                    username=user, name=name, mobile=mobile, gender=gender.upper(), profile_image=profile_image)
                                data.save()
                                return Response({"Success": "Registration Successfully"}, status=status.HTTP_200_OK)
                            else:
                                return Response({"Error": "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"Error": "Enter valid email address"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"Error": "Phone number already registered"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"Error": "User Already Exist with this email address"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Error": "Username length must be greater than 6"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "User Already Exist with this username"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def send_link(request):
    if request.method == "POST":
        email = request.POST['email']
        recipient_list = []
        if custom_user.objects.filter(email=email).exists():
            user_with_email = custom_user.objects.get(email=email)
            recipient_list.append(user_with_email.email)

            # Link = 'http://127.0.0.1:8001/forgot_password/'
            Link = 'http://3.144.89.49/forgot_password/'
            characters = string.ascii_letters + string.digits + string.punctuation
            token = ''.join(random.choice(characters) for i in range(50))
            user = custom_user.objects.get(email=email)
            user.confirm_token = token
            user.save()

            send_mail(
                'Forgot password',
                "Go to Link : " + Link + " and enter token : " + token,
                'demo.logixbuiltinfo@gmail.com',
                fail_silently=False,
                recipient_list=recipient_list
            )
            return Response({"Success": "Check Your email for Forgot Password"}, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "User Not Exist with this email address"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        user_token = request.POST['user_token']
        new_pass = request.POST['new_pass']
        confirm_pass = request.POST['confirm_pass']

        if custom_user.objects.filter(email=email).exists():
            if custom_user.objects.filter(confirm_token=user_token).exists():
                reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#$%&*+,-./:;<=>?@\^_`|~])[A-Za-z\d!#$%&*+,-./:;<=>?@\^_`|~]{6,20}$"
                pat = re.compile(reg)
                mat = re.search(pat, new_pass)
                if mat:
                    if new_pass == confirm_pass:
                        obj1 = custom_user.objects.get(
                            confirm_token=user_token)
                        obj1.set_password(new_pass)
                        obj2 = custom_user.objects.get(
                            confirm_token=user_token).profile
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
            return Response({"Error": "User Not Exist with this email address"}, status=status.HTTP_401_UNAUTHORIZED)


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
            return Response({"Error": "User Not Exist with this username"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']
        mobile = request.POST['mobile']
        gender = request.POST['gender']
        profile_image = request.FILES['profile_image']
        date_of_Birth = request.POST['dob']
        city = request.POST['city']
        country = request.POST['country']
        user_Latitude = request.POST['lat']
        user_Longitude = request.POST['long']
        snapchat = request.POST['snap']
        facebook = request.POST['fb']
        instagram = request.POST['insta']
        website = request.POST['website']
        avatar_image = request.FILES['avatar']
        bitmoji = request.FILES['bitmoji']

        user1 = authenticate(username=username, password=password)
        if user1:
            user = custom_user.objects.get(username=username).profile
            user.name = name
            user.mobile = mobile
            user.gender = gender
            user.profile_image = profile_image
            user.dob = date_of_Birth
            user.city = city
            user.country = country.upper()
            user.lat = user_Latitude
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
            return Response({"Error": "User Not Exist with this username and password"}, status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == "GET":
        username = request.GET['username']
        password = request.GET['password']
        user1 = authenticate(username=username, password=password)
        if user1.is_superuser:
            queryset = Profile.objects.all()
            serializer_class = RegistrationSerializer(queryset, many=True)
            return Response({'data': serializer_class.data}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': "You are not admin user"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def specific_user(request):
    if request.method == "GET":
        username = request.GET['username']
        queryset = Profile.objects.filter(username__username=username)
        serializer_class = RegistrationSerializer(queryset, many=True)
        return Response({'data': serializer_class.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_count(request):
    queryset = Profile.objects.all()
    serializer_class = RegistrationSerializer(queryset, many=True)
    return Response({'Total users': len(serializer_class.data)}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def genderwise(request):
    gen = request.GET['gender']
    obj1 = Profile.objects.filter(gender=gen.upper())
    serializer_class = RegistrationSerializer(obj1, many=True)
    return Response({f'Total users with {gen} gender': len(serializer_class.data)}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def countrywise(request):
    con = request.GET['country']
    obj1 = Profile.objects.filter(country=con.upper())
    serializer_class = RegistrationSerializer(obj1, many=True)
    return Response({f'Users with {con} country': serializer_class.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def details(request):
    if request.method == "POST":
        username = request.POST['username']
        signature = request.FILES['signature']
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

        user = custom_user.objects.get(username=username)
        try:
            if user:
                data = user_detail(username=user,
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
                return Response({"Success": "Details Added."}, status=status.HTTP_200_OK)
        except:
            details_obj = user_detail.objects.get(username=user.id)
            details_obj.signature = signature
            details_obj.export_quality = export_quality
            details_obj.Language = Language
            details_obj.user_stared_templates = user_stared_templates
            details_obj.user_stared_backgrounds = user_stared_backgrounds
            details_obj.user_stared_stickers = user_stared_stickers
            details_obj.user_stared_Textart = user_stared_Textart
            details_obj.user_stared_colors = user_stared_colors
            details_obj.user_stared_fonts = user_stared_fonts
            details_obj.most_used_fonts = most_used_fonts
            details_obj.user_custom_colors = user_custom_colors
            details_obj.instagram_follower = instagram_follower
            details_obj.grid_snapping = grid_snapping
            details_obj.user_recent_text = user_recent_text
            details_obj.appearance_mode = appearance_mode
            details_obj.enable_iCloud_backup = enable_iCloud_backup
            details_obj.save_projects_automatically = save_projects_automatically
            details_obj.save_projects_on_export = save_projects_on_export
            details_obj.notifications_permission = notifications_permission
            details_obj.inApp_notifications_permission = inApp_notifications_permission
            details_obj.photo_library_permission = photo_library_permission
            details_obj.digital_riyals_rewards = digital_riyals_rewards
            details_obj.enable_touch = enable_touch
            details_obj.app_theme = app_theme
            details_obj.always_crop = always_crop
            details_obj.save()
            return Response({"Success": "User details updated."}, status=status.HTTP_200_OK)
        else:
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
        iOS = request.POST['iOS']
        Device_Storage = request.POST['Device_Storage']
        Lunch_count = request.POST['Lunch_count']
        Push_Notification_Status = request.POST['Push_Notification_Status']
        Library_permission_Status = request.POST['Library_permission_Status']
        Latest_Geolocation = request.POST['Latest_Geolocation']
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
            app_data_obj.iOS = iOS
            app_data_obj.Device_Storage = Device_Storage
            app_data_obj.Lunch_count = Lunch_count
            app_data_obj.Push_Notification_Status = Push_Notification_Status
            app_data_obj.Library_permission_Status = Library_permission_Status
            app_data_obj.Latest_Geolocation = Latest_Geolocation
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
                                            iOS=iOS,
                                            Device_Storage=Device_Storage,
                                            Lunch_count=Lunch_count,
                                            Push_Notification_Status=Push_Notification_Status,
                                            Library_permission_Status=Library_permission_Status,
                                            Latest_Geolocation=Latest_Geolocation,
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
                return Response({"Error": "User not Found!!!"}, status=status.HTTP_401_UNAUTHORIZED)


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
            status = request.POST['status']
            auto_renew_status = request.POST['auto_renew_status']
            is_in_billing_retry_period = request.POST['is_in_billing_retry_period']
            is_in_intro_offer_period = request.POST['is_in_intro_offer_period']
            is_trial_period = request.POST['is_trial_period']

            user = custom_user.objects.get(username=username)
            if user:
                obj = Purchase(
                    username=user,
                    status=status,
                    auto_renew_status=auto_renew_status,
                    is_in_billing_retry_period=is_in_billing_retry_period,
                    is_in_intro_offer_period=is_in_intro_offer_period,
                    is_trial_period=is_trial_period
                )
                obj.save()
                return Response({"Success": "Data Added"}, status=status.HTTP_200_OK)
            else:
                return Response({"Error": "User Not Exist!!!"}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({"Error": "Record with same user exists"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        username = request.POST['username']
        status = request.POST['status']
        auto_renew_status = request.POST['auto_renew_status']
        is_in_billing_retry_period = request.POST['is_in_billing_retry_period']
        is_in_intro_offer_period = request.POST['is_in_intro_offer_period']
        is_trial_period = request.POST['is_trial_period']

        user = custom_user.objects.get(username=username)
        if user:
            purchase_obj = custom_user.objects.get(username=username).purchase
            purchase_obj.status = status
            purchase_obj.auto_renew_status = auto_renew_status
            purchase_obj.is_in_billing_retry_period = is_in_billing_retry_period
            purchase_obj.is_in_intro_offer_period = is_in_intro_offer_period
            purchase_obj.is_trial_period = is_trial_period
            purchase_obj.save()
            return Response({"Success": "Data Updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "User Not Exist!!!"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    if request.method == "POST":
        username = request.POST['username']
        user_obj = custom_user.objects.get(username=username)
        if user_obj:
            user_obj.is_active = False
            user_obj.delete_date = datetime.now()
            user_obj.save()

            return Response({"Success": "Your account is under deleting process and deleted in 30 days."}, status=status.HTTP_200_OK)
        else:
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
                    username = user_obj,
                    productID = productID,
                    product = product,
                    productPromo = productPromo,
                    promoPrice = promoPrice,
                    annaulSubProd = annaulSubProd,
                    annaulSub = annaulSub,
                    monthlySubProd = monthlySubProd,
                    monthlySub = monthlySub,
                    localeId = localeId
                )
                return Response({"Success": "Product Details Added."}, status=status.HTTP_200_OK)

            except:
                product1 = Product.objects.filter(product=product).first()
                print(product1)
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
            return Response({"Error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)