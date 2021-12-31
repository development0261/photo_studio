from django.contrib.auth import get_user_model, login, logout, authenticate
from .models import Registration, custom_user
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


custom_user = get_user_model()
reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#$%&*+,-./:;<=>?@\^_`|~])[A-Za-z\d!#$%&*+,-./:;<=>?@\^_`|~]{6,20}$"
for_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def index(request):
    return Response({"Message": "Welcome"})


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
    return Response({"Message": "Successfully Logged Out"})


@api_view(['GET', 'POST'])
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
            user_pat = re.compile(reg)
            user_mat = re.search(user_pat, Username)
            if user_mat:
                if not custom_user.objects.filter(email=Email).exists():
                    print(Email)
                    if(re.fullmatch(for_email, Email)):
                        pat = re.compile(reg)
                        mat = re.search(pat, Password)
                        if mat:
                            user = custom_user.objects.create_user(username=Username, password=Password, email=Email)
                            user.save()
                            data = Registration(username=user, name=Name, mobile=Mobile, gender=Gender, dob=Date_of_Birth, city=City, country=Country, lat=User_Latitude, long=User_Longitude, snap=Snapchat, fb=Facebook, insta=Instagram, website=website, profile=Profile_image, avatar=Avatar_image, bitmoji=Bitmoji)
                            data.save()
                            return Response({"Result": "Registration Successfully"})                        
                        else:
                            return Response({"Result": "Password must be include atleast one special character,number,small and capital letter and length between 6 to 20."})
                    else:
                        return Response({"Result": "Enter valid Email address"}) 
                else:
                    return Response({"Result": "User Already Exist with this Email address"})
            else:
                return Response({"Result": "Username must be include atleast one special character,number,small and capital letter and length between 6 to 20."})
        else:
            return Response({"Result": "User Already Exist with this username"})
    else:
        queryset = Registration.objects.all()
        serializer_class = RegistrationSerializer(queryset, many=True)
        return Response({'data': serializer_class.data})


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
                "Go to Link : " + Link + " and enter token : " + token,
                'demo.logixbuiltinfo@gmail.com',
                ['hegeha3495@saturdata.com'],
                fail_silently=False,
            )
            return Response({"Result": "Check Your Email-Box"})
        else:
            return Response({"Result": "User Not Exist with this Email address"})


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
                    if new_pass == confirm_pass :
                        u = custom_user.objects.get(confirm_token=user_token)
                        u.set_password(new_pass)
                        u.save()
                        return Response({"Result": "Password updated Successfully."})
                    else:
                        return Response({"Result": "new password and confirm password doesnot matched."})
                else:
                    return Response({"Result": "Password must be include atleast one special character,number,small and capital letter and length between 6 to 20."})
            else:
                return Response({"Result": "Oops!! Please check your Token"})
        else:
            return Response({"Result": "User Not Exist with this Email address"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        new_pass = request.POST['new_pass']
        confirm_pass = request.POST['confirm_pass']
        if custom_user.objects.filter(username=username).exists():
            print("yes")
            user = authenticate(username=username, password=password)
            if user:                
                pat = re.compile(reg)
                mat = re.search(pat, new_pass)
                if mat:
                    if new_pass == confirm_pass :
                        u = custom_user.objects.get(username=username)
                        u.set_password(new_pass)
                        u.save()
                        return Response({"Result": "Password updated Successfully."})
                    else:
                        return Response({"Result": "new password and confirm password doesnot matched."})
                else:
                    return Response({"Result": "Password must be include atleast one special character,number,small and capital letter and length between 6 to 20."})
            else:
                return Response({"Result": "Username and Password doesnot matched."})
        else:
            return Response({"Result": "User Not Exist with this username"})

