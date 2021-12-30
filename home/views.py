from django.contrib.auth import get_user_model, login, logout, authenticate
from .models import Registration,custom_user
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


custom_user = get_user_model()

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def index(request):
    return Response({"Message":"Welcome"})

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data

        for k,v in serializer.items():
            data[k] = v
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logoutProcess(request):
    logout(request)
    return Response({"Message":"Successfully Logged Out"})


@api_view(['GET','POST'])
def register(request):
    if request.method == "POST":
        Username = request.POST['username']
        Email = request.POST['email']
        Password = request.POST['password']
        Name = request.POST['name']
        Mobile = request.POST['mobile']
        Gender = request.POST['gender']
        Date_of_Birth = request.POST['dob']
        City = request.POST['city']
        Country = request.POST['country']
        User_Latitude = request.POST['lat']
        User_Longitude = request.POST['long']
        Snapchat = request.POST['snap']
        Facebook = request.POST['fb']
        Instagram = request.POST['insta']
        Profile_image = request.FILES['profile']
        website = request.POST['website']
        Avatar_image = request.FILES['avatar']
        Bitmoji = request.FILES['bitmoji']
        if not custom_user.objects.filter(username=Username).exists():
            if not custom_user.objects.filter(email=Email).exists():
                special = '!#$%&()*+,-./:;<=>?@[\]^_`{|}~'
                special_list=[]
                for i in Password:
                    if i in special:
                        special_list.append(i)
                if len(special_list) != 0:
                    user = custom_user(username=Username, password=Password, email=Email)
                    user.save()
                    data = Registration(username=user, name=Name, mobile=Mobile, gender=Gender, dob=Date_of_Birth, city=City, country=Country,
                                    lat=User_Latitude, long=User_Longitude, snap=Snapchat, fb=Facebook, insta=Instagram, website=website, profile=Profile_image, avatar=Avatar_image, bitmoji=Bitmoji)
                    data.save()
                    return Response({"Result":"Registration Successfully"})
                else:
                    return Response({"Result":"Please use one Special character for Password"})
            else:
                return Response({"Result":"User Already Exist with this Email address"})
        else:
            return Response({"Result":"User Already Exist with this username"})
    else:
        queryset = Registration.objects.all()
        serializer_class = RegistrationSerializer(queryset, many=True)
        return Response({'data':serializer_class.data})

@api_view(['POST'])
def send_link(request):
    if request.method == "POST":
        email = request.POST['email']
        if custom_user.objects.filter(email=email).exists():
            Link = 'http://127.0.0.1:8001/forgot_password/'
            characters = string.ascii_letters + string.digits + string.punctuation
            token = ''.join(random.choice(characters) for i in range(50))
            user = custom_user.objects.get(email=email)
            user.confirm_token = token
            user.save()

            send_mail( 
                    'Forgot Password',
                    "Go to Link : " + Link + " and enter token : " + token ,
                    'demo.logixbuiltinfo@gmail.com',
                    ['hegeha3495@saturdata.com'],
                    fail_silently=False,
                )
            return Response({"Result":"Check Your Email-Box"})
        else:
            return Response({"Result":"User Not Exist with this Email address"})

@api_view(['POST'])
def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        user_token = request.POST['user_token']
        new_pass = request.POST['new_pass']
        confirm_pass = request.POST['confirm_pass']

        if custom_user.objects.filter(email=email).exists():
            if custom_user.objects.filter(confirm_token=user_token).exists():
                if new_pass == confirm_pass:
                    user = custom_user.objects.get(confirm_token=user_token)
                    user.set_password(new_pass)
                    user.save()
                    return Response({"Result":"Update Password Successfully"})
                else:
                    return Response({"Result":"New Password and Confirm Password Doesnot matched."})
            else:
                    return Response({"Result":"Oops!! Please check your Token"})

        else:
            return Response({"Result":"User Not Exist with this Email address"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        new_pass = request.POST['new_pass']
        confirm_pass = request.POST['confirm_pass']

        if custom_user.objects.filter(username=username).exists():
            user = authenticate(username = username, password = password)
            if not user:
                return Response({"Result":"Username and Password doesnot matched."})
            elif new_pass != confirm_pass:
                return Response({"Result":"New Password and Confirm Password Doesnot matched."})
            else:
                u = custom_user.objects.get(username=username)
                u.set_password(new_pass)
                u.save()
            return Response({"Result":"Update Password Successfully"})
        else:
            return Response({"Result":"User Not Exist with this username"})
