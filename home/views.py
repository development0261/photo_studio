from django.contrib.auth import get_user_model, login, logout, authenticate
from django.shortcuts import render
from .models import Profile, user_preference, application_data, Purchase, Product, Tag,application_data_noauth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSerializer, UserSerializerWithToken, RegistrationSerializer, SocialSerializer, ProfileSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import random
import string
import re
from datetime import datetime, timedelta, date
import pytz
from rest_framework import status
from django.contrib.auth.hashers import check_password
import json
from django.contrib.auth.models import update_last_login
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Restrict media image
from django.views.static import serve
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

#get city and country
from geopy.geocoders import Nominatim
from pycountry import countries
import requests
from random import randint

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


# initialize Nominatim API
geolocator = Nominatim(user_agent="geoapiExercises")

@login_required
def protected_serve(request, path, document_root=None, show_indexes=False):
	return serve(request, path, document_root, show_indexes)

def unprotected_serve(request, path, document_root=None, show_indexes=False):
	return serve(request, path, document_root, show_indexes)
# end------------


User = get_user_model()
# reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#$%&*+,-./:;<=>?@\^_`|~])[A-Za-z\d!#$%&*+,-./:;<=>?@\^_`|~]{6,20}$"
reg = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{6,20}$"
for_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
punctuation = "!#$%&()*+, -.:;<=>?@[\]^_`{|}~"

#check time after user request for delete account
# users_obj = User.objects.filter(is_active=False)
# for row in users_obj:
# 	if row.delete_date + timedelta(days=30):
# 		users_obj.delete()
		
def main_index(request):
	return render(request,"main_index.html")

# for login
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		result = dict()
	
		if User.objects.filter(username=attrs['username']).exists():
			if not check_password(attrs['password'], User.objects.get(username=attrs['username']).password):
				result["value"] = False
				result['data']=None
				result["message"] = "Invalid Password"
				return result
			else:
				data = super().validate(attrs)
				serializer = UserSerializerWithToken(self.user).data
				for k, v in serializer.items():
					data[k] = v
				user_obj = authenticate(username=attrs['username'], password=attrs['password'])
				update_last_login(None, user_obj)
				try:
					profile = Profile.objects.create(username = user_obj)  
					profile = Profile.objects.filter(username = user_obj)
				except:
					profile = Profile.objects.filter(username = user_obj)
				
				serializer_class = ProfileSerializer(profile, many=True)
				   			
				for i,j in serializer_class.data[0].items():
					data[i]=j
				# data['country_code']=None
				del data['refresh']
				del data['access']
				result["value"] = True
				result['message']='success'
				result["data"] = data

				if user_obj.auth_token:
					if len(user_obj.auth_token)==3:
						user_obj.auth_token[0] = (str(result['data']['token']))
					else:
						user_obj.auth_token.append(str(result['data']['token']))
				else:
					user_obj.auth_token = "{"+str(result['data']['token'])+"}"
				user_obj.save()

				return result
		else:
			result["value"] = False
			result["message"] = "Account with this username is not exists"
			result["data"]=None
			return result

class MyTokenObtainPairView(TokenObtainPairView):
	serializer_class = MyTokenObtainPairSerializer
	

# for logout
@api_view(['GET'])

def logoutProcess(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result['data']=None
		return Response(result, status=status.HTTP_200_OK)

	user_obj = User.objects.get(auth_token__contains = "{" + header_token + "}")
	for i in user_obj.auth_token:
		if i == header_token:
			user_obj.auth_token.remove(i)

	user_obj.save()
	result["value"] = True
	result["message"] = "Successfully Logged Out"
	return Response(result, status=status.HTTP_200_OK)

# user registration
@api_view(['POST'])
def register(request):
	result = dict()
	if request.method == "POST":
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		name = request.POST.get('name')
		mobile = request.POST.get('mobile')
		gender = request.POST.get('gender')
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')

		if 'profile_image' in request.FILES:
			profile_image = request.FILES['profile_image']
		if 'avatar_image' in request.FILES:
			avatar_image = request.FILES['avatar_image']
		if not User.objects.filter(username=username).exists():
			if len(username) > 5:
				if not User.objects.filter(email=email).exists():
					if mobile != "" and mobile is not None:
						if not Profile.objects.filter(mobile=mobile).exists() and len(mobile) > 0:
							if(re.fullmatch(for_email, email)):
								pat = re.compile(reg)
								mat = re.search(pat, password)
								if mat:
									user = User.objects.create_user(
										username=username, password=password, email=email, first_name=first_name, last_name=last_name)
									user.save()

									data = Profile(
										username=user, name=name, mobile=mobile, gender=gender)
									if 'profile_image' in request.FILES:
										data.profile_image = profile_image
									if 'avatar_image' in request.FILES:
										data.avatar = avatar_image
									data.save()

									temp_obj = User.objects.get(username=username)                                                           
									pro_obj = Profile.objects.filter(username=temp_obj)

									if pro_obj[0].profile_image:
										img = pro_obj[0].profile_image
									else:
										img = ""
									if pro_obj[0].avatar:
										img1 = pro_obj[0].avatar
									else:
										img1 = ""
									if pro_obj[0].bitmoji:
										img2 = pro_obj[0].bitmoji
									else:
										img2 = ""
									
									serializer_class = UserSerializerWithToken(temp_obj)
									# creating dict for add profile response
									final_data = dict(serializer_class.data)
									profile_serializer_class = ProfileSerializer(pro_obj, many=True)

									# add profile data to response
									for i,j in profile_serializer_class.data[0].items():
										final_data[i]=j
									result["value"] = True
									result['message']="success"
									result["data"] = final_data

									headers = {
										'Content-Type': 'application/json'
									}

									if user.auth_token:
										if len(user.auth_token)==3:
											user.auth_token[0] = (str(result['data']['token']))
										else:
											user.auth_token.append(str(result['data']['token']))
									else:
										user.auth_token = "{"+str(result['data']['token'])+"}"
									user.save()

									return Response(result, headers=headers, status=status.HTTP_200_OK)
								else:
									result["value"] = False
									result["message"] = "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."
									result["data"]=None
									return Response(result, status=status.HTTP_200_OK)
							else:
								result["value"] = False
								result["message"] = "Enter valid email address"
								result["data"]=None
								return Response(result, status=status.HTTP_200_OK)
						else:
							result["value"] = False
							result["message"] = "Phone number already registered"
							result["data"]=None
       
							return Response(result, status=status.HTTP_200_OK)
					else:
						if(re.fullmatch(for_email, email)):
							pat = re.compile(reg)
							mat = re.search(pat, password)
							if mat:
								user = User.objects.create_user(
									username=username, password=password, email=email, first_name=first_name, last_name=last_name)
								user.save()

								data = Profile(
									username=user, name=name, mobile=mobile, gender=gender)
								if 'profile_image' in request.FILES:
									data.profile_image = profile_image
								data.save()

								temp_obj = User.objects.get(username=username)
								pro_obj = Profile.objects.filter(username=temp_obj)

								if pro_obj[0].profile_image:
									img = pro_obj[0].profile_image
								else:
									img = ""
								if pro_obj[0].avatar:
									img1 = pro_obj[0].avatar
								else:
									img1 = ""
								if pro_obj[0].bitmoji:
									img2 = pro_obj[0].bitmoji
								else:
									img2 = ""

								serializer_class = UserSerializerWithToken(temp_obj)
								# creating dict for add profile response
								final_data = dict(serializer_class.data)
								profile_serializer_class = ProfileSerializer(pro_obj, many=True)

								# add profile data to response
								for i,j in profile_serializer_class.data[0].items():
									final_data[i]=j
								final_data['country_code']=None
								result["value"] = True
								result["message"]='sucess'
								result["data"] = final_data

								if user.auth_token:
									if len(user.auth_token)==3:
										user.auth_token[0] = (str(result['data']['token']))
									else:
										user.auth_token.append(str(result['data']['token']))
								else:
									user.auth_token = "{"+str(result['data']['token'])+"}"
								user.save()

								return Response(result, status=status.HTTP_200_OK)
							else:
								result["value"] = False
								result["message"] = "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."
								result["data"]=None
								return Response(result, status=status.HTTP_200_OK)
						else:
							result["value"] = False
							result["message"] = "Enter valid email address!!!"
							return Response(result, status=status.HTTP_200_OK)
				else:
					result["value"] = False
					result["message"] = "User Already Exist with this email address!!!"
					result["data"]=None
					return Response(result, status=status.HTTP_200_OK)
			else:
				result["value"] = False
				result["message"] = "Username length must be greater than 6!!!"
				result["data"]=None
				return Response(result, status=status.HTTP_200_OK)
		else:
			result["value"] = False
			result["message"] = "User Already Exists!!!"
			result["data"]=None
			return Response(result, status=status.HTTP_200_OK)

# user registration using social media
@api_view(['POST'])
def social_media_registration(request):
	# try:
	result = dict()
	if request.method == "POST":
		username = request.POST['username']
		token = request.POST['token']
		social_media_site = request.POST['social_media_site']
		is_social = request.POST['is_social']

		if 'profile_image' in request.FILES:
			profile_image = request.FILES['profile_image']

		email = request.POST.get('email')
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		name = request.POST.get('name')
		city = request.POST.get('city')
		country = request.POST.get('country')
		latitude = request.POST.get('latitude')
		longitude = request.POST.get('longitude')

		if latitude:
			latitude = latitude
		else:
			latitude = None

		if longitude:
			longitude = longitude
		else:
			longitude = None

		if token:
			if social_media_site.lower()=="apple" or social_media_site.lower()=="snapchat":
				if not User.objects.filter(token=token).exists():
					user_obj = User.objects.create_user(
						username=username, password=token, email=email,
						token=token, social_media_site=social_media_site, first_name=first_name, last_name=last_name)
					user_obj.save()
					profile_obj = Profile(username=user_obj, is_social=is_social, name=name, city=city, country=country, lat=latitude, long=longitude)
					if 'profile_image' in request.FILES:
						profile_obj.profile_image = profile_image
					profile_obj.save()
					serializer_class = SocialSerializer(profile_obj)
					result["value"] = True
					result['message']='success'
					result["data"] = serializer_class.data

					if user_obj.auth_token:
						if len(user_obj.auth_token)==3:
							user_obj.auth_token[0] = (str(result['data']['token']))
						else:
							user_obj.auth_token.append(str(result['data']['token']))
					else:
						user_obj.auth_token = "{"+str(result['data']['token'])+"}"
					user_obj.save()

					return Response(result, status=status.HTTP_200_OK)
				else:
					user_obj = User.objects.get(token=token)
					if not user_obj.is_active:
						result["value"] = False
						result["data"]=None
						result["message"] = "Account with this username is not exists!"
						return Response(result, status=status.HTTP_200_OK)
					profile_obj = Profile.objects.get(username=user_obj)
					serializer_class = SocialSerializer(profile_obj)
					result["value"] = True
					result['message']='success'
					result["data"] = serializer_class.data

					if user_obj.auth_token:
						if len(user_obj.auth_token)==3:
							user_obj.auth_token[0] = (str(result['data']['token']))
						else:
							user_obj.auth_token.append(str(result['data']['token']))
					else:
						user_obj.auth_token = "{"+str(result['data']['token'])+"}"
					user_obj.save()

					return Response(result, status=status.HTTP_200_OK)

			elif social_media_site.lower()=="google":
				url = f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
				print(url)
				r = requests.get(url = url)
				data = r.json()

				if 'error' in data:
					result["value"] = False
					result["message"] = "Please check your token!"
					result["data"]=None
     
					return Response(result, status=status.HTTP_200_OK)
				social_id = data['sub']
			elif social_media_site.lower()=="facebook":
				url = f'https://graph.facebook.com/me?access_token={token}'
				r = requests.get(url = url)
				data = r.json()
				if 'error' in data:
					result["value"] = False
					result["message"] = "Please check your tokenbad!"
					result["data"]=None
					return Response(result, status=status.HTTP_200_OK)
				social_id = data['id']
			if not User.objects.filter(social_id=social_id).exists():
				if User.objects.filter(username=username).exists():
					result["value"] = False
					result["message"] = "User already exists with this username!"
					result["data"]=None
					return Response(result, status=status.HTTP_200_OK)

				user_obj = User.objects.create_user(
					username=username, password=token, email=email,
					token=token, social_media_site=social_media_site, social_id=social_id, first_name=first_name, last_name=last_name)
				user_obj.save()

				profile_obj = Profile(username=user_obj, is_social=is_social, name=name, city=city, country=country, lat=latitude, long=longitude)
				if 'profile_image' in request.FILES:
					profile_obj.profile_image = profile_image
				profile_obj.save()
				serializer_class = SocialSerializer(profile_obj)
				result["value"] = True
				result["message"]='success'
				result["data"] = serializer_class.data

				if user_obj.auth_token:
					if len(user_obj.auth_token)==3:
						user_obj.auth_token[0] = (str(result['data']['token']))
					else:
						user_obj.auth_token.append(str(result['data']['token']))
				else:
					user_obj.auth_token = "{"+str(result['data']['token'])+"}"
				user_obj.save()

				return Response(result, status=status.HTTP_200_OK)
			else:
				user_obj = User.objects.get(social_id=social_id)
				if not user_obj.is_active:
					result["value"] = False
					result["message"] = "Account with this username is not exists!"
					result["data"]=None
					return Response(result, status=status.HTTP_200_OK)
				profile_obj = Profile.objects.get(username=user_obj)
				serializer_class = SocialSerializer(profile_obj)
				result["value"] = True
				result["message"]='success'
				result["data"] = serializer_class.data

				if user_obj.auth_token:
					if len(user_obj.auth_token)==3:
						user_obj.auth_token[0] = (str(result['data']['token']))
					else:
						user_obj.auth_token.append(str(result['data']['token']))
				else:
					user_obj.auth_token = "{"+str(result['data']['token'])+"}"
				user_obj.save()
				print(result)
				return Response(result, status=status.HTTP_200_OK)

	else:
		result["value"] = False
		result["message"] = "Method not Allowed!"
		result["data"]=None
		return Response(result,status=status.HTTP_405_METHOD_NOT_ALLOWED)
	# except Exception as e:
	# 	print(e)
	# 	result["value"] = False
	# 	result["message"] = "Something went wrong! Please contact to support team."
	# 	return Response(result,status=status.HTTP_200_OK)
	
# send email for forgot password
@api_view(['POST'])
def send_link(request):
	result = dict()
	if request.method == "POST":
		email = request.POST['email']
		recipient_list = []

		if User.objects.filter(email=email).exists():
			try:
				u_obj = User.objects.get(email=email).profile
			except:
				user_obj = User.objects.get(email=email)
				p_obj = Profile.objects.create(username = user_obj)
				p_obj.save()
				u_obj = User.objects.get(email=email).profile

			if u_obj.count_for_forgot_pass < 5:
				if u_obj.time_for_forgot_pass is None:
					pass
				elif (u_obj.time_for_forgot_pass + timedelta(hours=1)) < pytz.utc.localize(datetime.now()):
					u_obj.count_for_forgot_pass = 0
					u_obj.save()
				user_with_email = User.objects.get(email=email)
				recipient_list.append(user_with_email.email)

				# Link = 'http://127.0.0.1:8000/home/reset-password'
				# Link = 'https://kitaba.me/home/reset-password'
				Link = "https://kitapa.app/reset/#/reset-password"             
				characters = string.ascii_letters + string.digits
				token = ''.join(random.choice(characters) for i in range(50))
				user = User.objects.get(email=email)
				user.confirm_token = token
				user.save()
				u_obj.expiration_date = pytz.utc.localize(datetime.now())
				u_obj.save()

				subject = 'Forgot Password'
				html_message = render_to_string(
					'mail_template.html', {'token': f'{Link}?token={token}&email={email}'})
				plain_message = strip_tags(html_message)
				from_email = 'From <no-reply@3rabapp.com>'
				to = recipient_list[0]

				mail.send_mail(subject, plain_message, from_email,
							[to], html_message=html_message)

				u_obj.count_for_forgot_pass += 1
				if u_obj.count_for_forgot_pass == 1:
					u_obj.time_for_forgot_pass = pytz.utc.localize(datetime.now())
				u_obj.save()

				data = {"Success": "Check Your email for Forgot Password", "count": u_obj.count_for_forgot_pass}

				result["value"] = True
				result["message"]='success'
				result["data"] = data
				return Response(result, status=status.HTTP_200_OK)
			elif u_obj.count_for_forgot_pass >= 5:
				if (u_obj.time_for_forgot_pass + timedelta(hours=1)) < pytz.utc.localize(datetime.now()):
					user_with_email = User.objects.get(email=email)
					recipient_list.append(user_with_email.email)

					# Link = 'http://127.0.0.1:8000/home/reset-password'
					# Link = 'https://kitaba.me/home/reset-password'
					Link = "https://kitapa.app/reset/#/reset-password"
					characters = string.ascii_letters + string.digits
					token = ''.join(random.choice(characters) for i in range(50))
					user = User.objects.get(email=email)
					user.confirm_token = token
					user.save()
					u_obj.expiration_date = pytz.utc.localize(datetime.now())
					u_obj.save()

					subject = 'Forgot Password'
					html_message = render_to_string(
						'mail_template.html', {'token': f'{Link}?token={token}&email={email}'})
					plain_message = strip_tags(html_message)
					from_email = 'From <no-reply@3rabapp.com>'
					to = recipient_list[0]  

					mail.send_mail(subject, plain_message, from_email,
								[to], html_message=html_message)

					u_obj.count_for_forgot_pass = 1
					if u_obj.count_for_forgot_pass == 1:
						u_obj.time_for_forgot_pass = pytz.utc.localize(datetime.now())
					u_obj.save()

					data = {"Success": "Check Your email for Forgot Password", "count": u_obj.count_for_forgot_pass}
					result["value"] = True
					result["message"]='success'
					result["data"] = data
					return Response(result, status=status.HTTP_200_OK)
				else:
					result["value"] = False
					result["message"] = "You have too many attempts in an Hour!!!You can try after an Hour."
					result["data"]=None
					return Response(result)
		else:
			result["value"] = False
			result["message"] = "User Not Exist with this email address"
			result["data"]=None
			return Response(result,status=status.HTTP_200_OK)

# reset-password 
@api_view(['GET'])
def reset_password(request):
	print("hiiiiiiiii")
	result = dict()
	token = request.GET.get('token')
	if request.method == "GET":
		email = request.GET['email']
		new_pass = request.GET['new_pass']
		confirm_pass = request.GET['confirm_pass']

		try:
			token_obj = User.objects.get(email=email)
			if token_obj.confirm_token != None :
				if token_obj.confirm_token!="token_expired":
					if len(token_obj.confirm_token) > 7:
						profile_obj = User.objects.get(email=email).profile
						if (profile_obj.expiration_date + timedelta(days=1))>pytz.utc.localize(datetime.now()):
							if User.objects.filter(email=email).exists():
								if User.objects.filter(confirm_token=token).exists():
									reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!#$%&*+,-./:;<=>?@\^_`|~])[A-Za-z\d!#$%&*+,-./:;<=>?@\^_`|~]{6,20}$"
									pat = re.compile(reg)
									mat = re.search(pat, new_pass)
									if mat:
										if new_pass == confirm_pass:
											obj1 = User.objects.get(
												confirm_token=token)
											obj1.set_password(new_pass)
											obj1.save()
											try:
												obj2 = Profile.objects.get(username=obj1.id)
												obj2.pass_forgot = datetime.now()
												obj2.save()
											except:
												profile_obj = Profile.objects.create(username=obj1, pass_forgot=datetime.now())
											obj1.confirm_token="token_expired"
											obj1.save()
											result["value"] = True
											result["message"]='success'
											result["message"] =  "Password updated Successfully."
											return Response(result, status=status.HTTP_200_OK)
										else:
											result["value"] = False
											result["message"] = "New password and confirm password doesnot matched."
											result["data"]=None
											return Response(result, status=status.HTTP_200_OK)
									else:
										result["value"] = False
										result["message"] = "Password must be include atleast one special character,number,small and capital letter and length between 6 to 20."
										result["data"]=None
										return Response(result, status=status.HTTP_200_OK)
								else:
									result["value"] = False
									result["message"] = "Oops!! Please check your Token"
									result["data"]=None
									return Response(result, status=status.HTTP_200_OK)
							else:
								result["value"] = False
								result["message"] = "User Not Exist with this email address"
								result["data"]=None
								return Response(result, status=status.HTTP_200_OK)
						else:
							result["value"] = False
							result["message"] = "Oops! Your Token is Expired!!!"
							result["data"]=None
							return Response(result, status=status.HTTP_200_OK)
					else:
						result["value"] = False
						result["message"] = "Please check your Token!!!"
						result["data"]=None
						return Response(result, status=status.HTTP_200_OK)
				else:
					result["value"] = False
					result["message"] = "You have changed your password once through your this token!"
					result["data"]=None
					return Response(result, status=status.HTTP_200_OK)
			else:
				result["value"] = False
				result["message"] = "Please check your Token!!!"
				result["data"]=None
				return Response(result, status=status.HTTP_200_OK)
		except:
			result["value"] = False
			result["message"] = "User Not Exist with this email address"
			result["data"]=None
			return Response(result, status=status.HTTP_200_OK)
	else:
		result["value"] = False
		result["message"] = "Method Not Allowed!!!"
		result["data"]=None
		return Response(result, status=status.HTTP_405_METHOD_NOT_ALLOWED)
				
# update-password
@api_view(['POST'])
def update_password(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result["data"]=None
		return Response(result, status=status.HTTP_200_OK)
	if request.method == "POST":
		password = request.POST['password']
		new_pass = request.POST['new_pass']
		confirm_pass = request.POST['confirm_pass']
		
		if User.objects.filter(username=request.user).exists():
			user = authenticate(username=request.user, password=password)
			if user:
				if user.check_password(new_pass):
					result["value"] = False
					result["message"] = "Old Password and New Password must be diffrent"
					result["data"]=None
					return Response(result, status=status.HTTP_200_OK)

				pat = re.compile(reg)
				mat = re.search(pat, new_pass)
				if mat:
					if new_pass == confirm_pass:
						user.set_password(new_pass)
						obj2 = User.objects.get(
							username=request.user).profile
						obj2.pass_update = date.today()
						user.save()
						obj2.save()
						# result["value"] = True
						# result["message"]='success'
						serializer_class = UserSerializerWithToken(user)
						# creating dict for add profile response
						final_data = dict(serializer_class.data)
						
						profile_serializer_class = ProfileSerializer(obj2)
						for i,j in profile_serializer_class.data.items():
							final_data[i]=j
						result["value"] = True
						result["message"]='success'
						result["data"] = final_data

						if user.auth_token:
							if len(user.auth_token)==3:
								user.auth_token[0] = (str(result['data']['token']))
							else:
								user.auth_token.append(str(result['data']['token']))
						else:
							user.auth_token = "{"+str(result['data']['token'])+"}"
						user.save()
						
						return Response(result, status=status.HTTP_200_OK)
					else:
						result["value"] = False
						result["message"] = "New password and confirm password doesnot matched."
						result["data"]=None
						return Response(result, status=status.HTTP_200_OK)
				else:
					result["value"] = False
					result["message"] = "Password must be include atleast one special character,number,small and capital letter and length between 6 to 20."
					result["data"]=None
					return Response(result, status=status.HTTP_200_OK)
			else:
				result["value"] = False
				result["message"] = "Password Not matched!!!"
				result["data"]=None
				return Response(result, status=status.HTTP_200_OK)
		else:
			result["value"] = False
			result["message"] = "User Not Exist with this username"
			result["data"]=None
			return Response(result, status=status.HTTP_200_OK)

# edit profile
@api_view(['POST'])
def profile(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result['data']=None
     	# result['data']=None
		print("result###-----",result)
		return Response(result, status=status.HTTP_200_OK)
	# try:
	
	user_obj = User.objects.get(auth_token__contains = "{" + header_token + "}")

	if request.method == "POST":
		email = request.POST.get('email')
		username = request.POST.get('username')
		name = request.POST.get('name')
		mobile = request.POST.get('mobile')
		gender = request.POST.get('gender')
		date_of_Birth = request.POST.get('dob')
		user_Latitude = request.POST.get('lat')
		user_Longitude = request.POST.get('long')
		snapchat = request.POST.get('snap')
		facebook = request.POST.get('fb')
		instagram = request.POST.get('insta')
		website = request.POST.get('website')
		city = ""
		country = ""
		country_code = request.POST.get('country_code')
		# g = geocoder.osm([user_Latitude,user_Longitude], method='reverse')
		
		if user_Latitude and user_Longitude:
			access_token="pk.eyJ1IjoiYXJhYmFwcCIsImEiOiJjbDh2YmtiODQwNXo4M29udTA0eWxldmIxIn0.tzc8bwS-5vvdE32_T0EY7A"
			url="https://api.mapbox.com/geocoding/v5/mapbox.places/"+user_Longitude+","+user_Latitude+".json?types=poi&access_token="+access_token

			resp = requests.get(url)
			if resp.status_code==200:
				data = json.loads(resp.content.decode())
				for i,j in data.items():
					if i=="features":
						for k in j:
							city=k['context'][-3]['text']
							country=(k['context'][-1]['text'])
			# location = geolocator.reverse(user_Latitude+","+user_Longitude)
			# address = location.raw['address']
			# country = address.get('country', '')
			# country_code = countries.get(name=country).alpha_2
		try:
			if date_of_Birth in request.POST:
				datetime.strptime(date_of_Birth, '%Y-%m-%d')
		except ValueError:
			result["value"] = False
			result["message"] = "date_of_Birth in incorrect date format. It should be YYYY-MM-DD"
			# result["data"]=None
			return Response(result, status=status.HTTP_200_OK)

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

		if user_obj.username != username:
			if User.objects.filter(username=username).exists():
				return Response({"Error": "username already taken!!!"}, status=status.HTTP_200_OK)

		if user_obj.email != email and email is not None:
			if(re.fullmatch(for_email, str(email))):
				if User.objects.filter(email=email).exists():
					result["value"] = False
					result["message"] = "Email already in use!!!"
					result['data']=None
     				
					return Response(result, status=status.HTTP_200_OK)
			else:
				result["value"] = False
				result["message"] = "Enter valid email address"
				result['data']=None

				return Response(result, status=status.HTTP_200_OK)

		if username:
			user_obj.username = username
			user_obj.save()
		profile_obj = Profile.objects.get(username=user_obj.id)
		profile_obj.name = name
		if email:
			user_obj.email = email
		if mobile:
			profile_obj.mobile = mobile
		if gender:
			profile_obj.gender = gender
		profile_obj.profile_image = profile_image
		if date_of_Birth !="":
			profile_obj.dob = date_of_Birth
		if city:
			profile_obj.city = city
		if country:
			profile_obj.country = country
		if user_Latitude != "":
			profile_obj.lat = user_Latitude
		if user_Longitude != "":
			profile_obj.long = user_Longitude
		if snapchat:
			profile_obj.snap = snapchat
		if facebook:
			profile_obj.fb = facebook
		if instagram:
			profile_obj.insta = instagram
		if website:
			profile_obj.website = website
		profile_obj.avatar = avatar_image
		profile_obj.bitmoji = bitmoji
		profile_obj.updated_at = datetime.now()
		print(country_code)
		if country_code:
			profile_obj.country_code = country_code
		else:
			profile_obj.country_code = None
		profile_obj.save()
		user_obj.save()

		serializer_class = UserSerializerWithToken(user_obj)
		# creating dict for add profile response
		final_data = dict(serializer_class.data)
		
		profile_serializer_class = ProfileSerializer(profile_obj)
		for i,j in profile_serializer_class.data.items():
			final_data[i]=j
		final_data['country_code']=country_code
		result["value"] = True
		result["data"] = final_data

		if user_obj.auth_token:
			if len(user_obj.auth_token)==3:
				user_obj.auth_token[0] = (str(result['data']['token']))
			else:
				user_obj.auth_token.append(str(result['data']['token']))
		else:
			user_obj.auth_token = "{"+str(result['data']['token'])+"}"
		user_obj.save()
		return Response(result, status=status.HTTP_200_OK)
	# except Exception as e:
	# 	print(e)
	# 	result["value"] = False
	# 	result["message"] = "Something went wrong! Please contact to support team."
	# 	return Response(result, status=status.HTTP_200_OK)

# get specific user

@api_view(['GET'])
def specific_user(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
	except KeyError:
		print("inside except====>")
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result['data']=None
		return Response(result, status=status.HTTP_200_OK)
	
	# request.user="Testing"
	queryset = Profile.objects.filter(username__username=request.user)
	serializer_class = ProfileSerializer(queryset, many=True)

	if serializer_class.data==[]:
			result["value"] = False
			result["message"] = "No Data Found!"
			result['data']=None
	else:
			result['value']= True
			result['message']='success'
			result['data'] = serializer_class.data[0]
	return Response(result, status=status.HTTP_200_OK)
		# queryset = Profile.objects.filter(username__username=request.user)
		# print("queryset:",queryset)
		# serializer_class = ProfileSerializer(queryset, many=True)

		# if serializer_class.data==[]:
		# 	result["value"] = False
		# 	result["message"] = "No Data Found!"
		# 	result['data']=None
		# else:
		# 	print(serializer_class.data)
		# 	result['value']= True
		# 	result['message']='success'
		# 	result['data'] = serializer_class.data[0]
		# return Response(result, status=status.HTTP_200_OK)

# get total user
@api_view(['POST'])
def user_count(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
	except KeyError:
		result['data']=None
		result["value"] = False
		result["message"] = "Please enter auth token!"
		return Response(result, status=status.HTTP_200_OK)
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer(queryset, many=True)
	
	if serializer_class.data==[]:
			result["value"] = False
			result["message"] = "Please enter auth token!"
			result['data']=None
	else:
			result['value']= True
			result['message']='success'
			result['data'] = f'Total users '+str(len(serializer_class.data))
	
	return Response(result, status=status.HTTP_200_OK)

# total user with specific gender
@api_view(['GET'])
def genderwise(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result["data"]=None
		return Response(result, status=status.HTTP_200_OK)
	gen = request.GET['gender']
	obj1 = Profile.objects.filter(gender__iexact=gen)
	serializer_class = ProfileSerializer(obj1, many=True)
	data=f'Total users with {gen} gender '+str(len(serializer_class.data))
	return Response({'value':True,'message':'success',"data": data}, status=status.HTTP_200_OK)

# total user with specific country
@api_view(['GET'])
def countrywise(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result['data']=None
		return Response(result, status=status.HTTP_200_OK)
	con = request.GET['country']
	obj1 = Profile.objects.filter(country__iexact=con)
	serializer_class = ProfileSerializer(obj1, many=True)
	data=f'Users with {con} country '+str(serializer_class.data)
	return Response({'value':True,'message':'success','data': data}, status=status.HTTP_200_OK)

# add and edit user preferences
@api_view(['POST'])
def preferences(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]

		if request.method == "POST":
			export_quality = request.POST['export_quality']
			Language = request.POST.get('Language')
			user_stared_templates = request.POST.get('user_stared_templates')
			user_stared_backgrounds = request.POST.get('user_stared_backgrounds')
			user_stared_stickers = request.POST.get('user_stared_stickers')
			user_stared_Textart = request.POST.get('user_stared_Textart')
			user_stared_colors = request.POST.get('user_stared_colors')
			user_stared_fonts = request.POST.get('user_stared_fonts')
			most_used_fonts = request.POST.get('most_used_fonts')
			user_custom_colors = request.POST.get('user_custom_colors')
			instagram_follower = request.POST.get('instagram_follower')
			grid_snapping = request.POST.get('grid_snapping')
			user_recent_text = request.POST.get('user_recent_text')
			appearance_mode = request.POST['appearance_mode']
			enable_iCloud_backup = request.POST.get('enable_iCloud_backup')
			save_projects_automatically = request.POST.get('save_projects_automatically')
			save_projects_on_export = request.POST.get('save_projects_on_export')
			notifications_permission = request.POST.get('notifications_permission')
			inApp_notifications_permission = request.POST.get('inApp_notifications_permission')
			photo_library_permission = request.POST.get('photo_library_permission')
			digital_riyals_rewards = request.POST.get('digital_riyals_rewards')
			enable_touch = request.POST.get('enable_touch')
			app_theme = request.POST['app_theme']
			always_crop = request.POST.get('always_crop')

			if 'signature' in request.FILES:
				signature = request.FILES['signature']
			else:
				signature = None

			if instagram_follower:
				instagram_follower = instagram_follower
			else:
				instagram_follower = False

			if grid_snapping:
				grid_snapping = grid_snapping
			else:
				grid_snapping = False

			if enable_iCloud_backup:
				enable_iCloud_backup = enable_iCloud_backup
			else:
				enable_iCloud_backup = False

			if save_projects_automatically:
				save_projects_automatically = save_projects_automatically
			else:
				save_projects_automatically = False

			if save_projects_on_export:
				save_projects_on_export = save_projects_on_export
			else:
				save_projects_on_export = False

			if notifications_permission:
				notifications_permission = notifications_permission
			else:
				notifications_permission = False

			if inApp_notifications_permission:
				inApp_notifications_permission = inApp_notifications_permission
			else:
				inApp_notifications_permission = False

			if photo_library_permission:
				photo_library_permission = photo_library_permission
			else:
				photo_library_permission = False

			if enable_touch:
				enable_touch = enable_touch
			else:
				enable_touch = False

			if always_crop:
				always_crop = always_crop
			else:
				always_crop = False			

		try:
			user_obj = User.objects.get(auth_token__contains = "{" + header_token + "}")
			try:
				if user_obj:
					data = user_preference(username=user_obj,
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
					result["value"] = True
					result["message"] = "preferences Added."
					return Response(result, status=status.HTTP_200_OK)
			except Exception as e:
				preferences_obj = user_preference.objects.get(username=user_obj.id)
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
				result["value"] = False
				result["message"] = "User preferences updated."
				result['data'] = None
				return Response(result, status=status.HTTP_200_OK)
		except Exception as e:
			result["value"] = False
			result["message"] = "User not Found!!!"
			result['data']=None
			return Response(result, status=status.HTTP_200_OK)
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result['data'	]=None
		return Response(result, status=status.HTTP_200_OK)

# add and edit application data
@api_view(['POST'])
def app_data(request):
	result = dict()
	try:
     	
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
		if request.method == "POST":
			UID = request.POST['UID']
			inApp_Products = request.POST.get('inApp_Products')
			Purchase_date = request.POST.get('Purchase_date')
			Purchased_product = request.POST.get('Purchased_product')
			Device_Model = request.POST.get('Device_Model')
			operating_system = request.POST.get('operating_system')
			Device_Storage = request.POST.get('Device_Storage')
			Lunch_count = request.POST.get('Lunch_count')
			Push_Notification_Status = request.POST.get('Push_Notification_Status')
			Library_permission_Status = request.POST.get('Library_permission_Status')
			latitude = request.POST.get('latitude')
			longitude = request.POST.get('longitude')
			Carrier = request.POST.get('Carrier')
			App_Last_Opened = request.POST.get('App_Last_Opened')
			Purchase_attempts = request.POST.get('Purchase_attempts')
			Grace_Period = request.POST.get('Grace_Period')
			Remaining_grace_period_days = request.POST.get('Remaining_grace_period_days')
			Number_of_projects = request.POST.get('Number_of_projects')
			Total_time_spent = request.POST.get('Total_time_spent')
			total_ads_served = request.POST.get('total_ads_served')
			Registered_user = request.POST.get('Registered_user')
			Push_Notification_token = request.POST.get('Push_Notification_token')

			if Push_Notification_Status:
				Push_Notification_Status = Push_Notification_Status
			else:
				Push_Notification_Status = False

			if Library_permission_Status:
				Library_permission_Status = Library_permission_Status
			else:
				Library_permission_Status = False

			if Registered_user:
				Registered_user = Registered_user
			else:
				Registered_user = False

			try:
				if Purchase_date:
					datetime.strptime(Purchase_date, '%Y-%m-%d')
			except ValueError:
				result["value"] = False
				result["message"] = "Purchase_date in incorrect date format. It should be YYYY-MM-DD"
				result['data']=None
				return Response(result, status=status.HTTP_200_OK)

			try:
				if App_Last_Opened:
					datetime.strptime(App_Last_Opened, '%Y-%m-%d')
			except ValueError:
				result["value"] = False
				result["message"] = "App_Last_Opened in incorrect date format. It should be YYYY-MM-DD"
				result['data']=None
				return Response(result, status=status.HTTP_200_OK)
			try:
				user = User.objects.get(auth_token__contains = "{" + header_token + "}")
				if application_data.objects.filter(username=user).exists():
					if application_data.objects.filter(UID = UID).exists():
						try:
							app_data_obj = application_data.objects.get(username =user, UID = UID)
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
							app_data_obj.no_auth='False'
							app_data_obj.save()
							return Response({"value":True,"message": "Details Updated."}, status=status.HTTP_200_OK)
						except Exception as e:
							return Response({"value":False,"message": "UID Exists!!!",'data':None}, status=status.HTTP_409_CONFLICT)
					else:
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
						return Response({"value":True,'message':'success',"message": "Details Added."}, status=status.HTTP_200_OK)


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
				return Response({"value":True,"message": "Details Added."}, status=status.HTTP_200_OK)
			except Exception as e:
				return Response({"value":False,"message": "User not Found!!!",'data':None}, status=status.HTTP_200_OK)
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result['data']=None
		return Response(result, status=status.HTTP_200_OK)
			
# check whether email is available or not
@api_view(['GET'])
def email_verification(request):
	result = dict()
	if request.method == "GET":
		email = request.GET['email']
		try:
			user = User.objects.get(email=email)
			result["value"] = False
			result["message"] = "Email is already registered!"
			result['data']=None
			return Response(result, status=status.HTTP_200_OK)
		except:
			result["value"] = True
			result["message"]= "Email is available."
			result['data']=None
			return Response(result, status=status.HTTP_200_OK)

# check whether username is available or not
@api_view(['GET'])
def username_verification(request):
	result = dict()
	if request.method == "GET":
		username = request.GET['username']
		try:
			user = User.objects.get(username=username)
			result["value"]=False
			result["message"]="Username already in use!!!"
			result['data']=None
   			# result['data']=None
			return Response(result, status=status.HTTP_200_OK)
		except:
			result["value"]=True
			result["message"]="Username is available."
			result['data']=None
			return Response(result, status=status.HTTP_200_OK)

# add and update purchase history
@api_view(['POST'])
def purchase_history(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
	
		if request.method == "POST":
			product = request.POST['product']
			pstatus = request.POST['pstatus']
			auto_renew_status = request.POST.get('auto_renew_status')
			is_in_billing_retry_period = request.POST.get('is_in_billing_retry_period')
			is_in_intro_offer_period = request.POST.get('is_in_intro_offer_period')
			is_trial_period = request.POST.get('is_trial_period')
			start_date = request.POST.get('start_date')
			end_date = request.POST.get('end_date')
			subscription_type = request.POST.get('subscription_type')
			try:
				if start_date:
					datetime.strptime(start_date, '%Y-%m-%d')
			except ValueError:
				result["value"]=False
				result['data']=None
				result["message"]="start_date in incorrect date format. It should be YYYY-MM-DD"
				return Response(result, status=status.HTTP_200_OK)		
			try:
				if end_date:
					datetime.strptime(end_date, '%Y-%m-%d')
			except ValueError:
				result["value"]=False
				result['data']=False
				result["message"]="end_date in incorrect date format. It should be YYYY-MM-DD"
				return Response(result, status=status.HTTP_200_OK)

			try:
				product_obj = Product.objects.get(product=product)
			except ObjectDoesNotExist:
				result["value"]=False
				result['data']=None
				result["message"]="Product does not exists!"
				return Response(result, status=status.HTTP_200_OK)

			try:
				user = User.objects.get(auth_token__contains = "{" + header_token + "}")
				# try:
				# 	purchase_obj = Purchase.objects.get(username=user.id)
				# 	purchase_obj.product = product_obj
				# 	purchase_obj.pstatus = pstatus
				# 	purchase_obj.auto_renew_status = auto_renew_status
				# 	purchase_obj.is_in_billing_retry_period = is_in_billing_retry_period
				# 	purchase_obj.is_in_intro_offer_period = is_in_intro_offer_period
				# 	purchase_obj.is_trial_period = is_trial_period
				# 	purchase_obj.start_date = start_date
				# 	purchase_obj.end_date = end_date
				# 	purchase_obj.subscription_type = subscription_type
				# 	purchase_obj.save()
				# 	result["value"]=True
				# 	result["message"]= "Data Updated"
				# 	return Response(result, status=status.HTTP_200_OK)
				# except Exception as e:
				obj = Purchase(
					username=user,
					product = product_obj,
					purchase_id = random_with_N_digits(10),
					pstatus=pstatus,
					auto_renew_status=auto_renew_status,
					is_in_billing_retry_period=is_in_billing_retry_period,
					is_in_intro_offer_period=is_in_intro_offer_period,
					is_trial_period=is_trial_period,
					start_date=start_date,
					end_date=end_date,
					subscription_type=subscription_type
				)
				obj.save()
				result["value"]=True
				result["message"]="Data Added"
				result['data']=obj
				return Response(result, status=status.HTTP_200_OK)
			except Exception as e:
				result["value"]=False
				result["message"]="User Not Exist!!!"
				result['data']=None
				return Response(result, status=status.HTTP_200_OK)
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result['data']=None
		return Response(result, status=status.HTTP_200_OK)			

# delete account
@api_view(['POST'])
def delete_account(request):
   
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result['data']= None
		return Response(result, status=status.HTTP_200_OK)
	if request.method == "POST":
		try:
			# password = request.POST.get('password')
			user_obj = User.objects.get(auth_token__contains = "{" + header_token + "}")
			
			# if user_obj.profile.is_social:
			user_obj.is_active = False
			user_obj.delete_date = datetime.now()
			user_obj.save()
			result["value"] = True
			result["message"] = "Your account is under deleting process and deleted in 30 days."
			return Response(result, status=status.HTTP_200_OK)

			# if not password:
			# 	result["value"] = False
			# 	result["message"] = "Password required for Delete Account!"
			# 	return Response(result, status=status.HTTP_200_OK)
			# if user_obj.check_password(password):
			# 	user_obj.is_active = False
			# 	user_obj.delete_date = datetime.now()
			# 	user_obj.save()
			# 	result["value"] = True
			# 	result["message"] = "Your account is under deleting process and deleted in 30 days."
			# 	return Response(result, status=status.HTTP_200_OK)
			# else:
				# result["value"] = False
				# result["message"] = "Incorrect Password!"
				# return Response(result, status=status.HTTP_200_OK)
		except Exception as e:
			result["value"] = False
			result["message"] = "User not found"
			result['data']=None
			return Response(result, status=status.HTTP_200_OK)

# add and update products
@api_view(['POST'])
def product(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
	
		if request.method == "POST":
			productID = request.POST['productID']
			product = request.POST['product']
			productPromo = request.POST.get('productPromo')
			promoPrice = request.POST.get('promoPrice')
			annaulSubProd = request.POST.get('annaulSubProd')
			annaulSub = request.POST.get('annaulSub')
			monthlySubProd = request.POST.get('monthlySubProd')
			monthlySub = request.POST.get('monthlySub')
			localeId = request.POST.get('localeId')

			try:
				product1 = Product.objects.get(product=product, productID=productID)
				product1.productPromo = productPromo
				product1.promoPrice = promoPrice
				product1.annaulSubProd = annaulSubProd
				product1.annaulSub = annaulSub
				product1.monthlySubProd = monthlySubProd
				product1.monthlySub = monthlySub
				product1.localeId = localeId
				product1.save()
				result["value"] = True
				result["message"] = "Product Details Updated."
				return Response(result, status=status.HTTP_200_OK)
			except Exception as e:
				if Product.objects.filter(productID=productID).exists() or Product.objects.filter(product=product).exists():
					result["value"] = False
					result["message"] = "Product or ProductID already exists!"
					return Response(result, status=status.HTTP_200_OK)

				product1 = Product.objects.create(
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
				result["value"] = True
				result["message"] = "Product Details Added."
				return Response(result, status=status.HTTP_200_OK)	
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result['data']=None
		return Response(result, status=status.HTTP_200_OK)

# load script
@api_view(['POST'])
def load_script(request):
	result = dict()
	if request.method == "POST":
		mydata = json.loads(request.body)
		username  = mydata.get('username')
		password  = mydata.get('password')
		email  = mydata.get('email')

		if not User.objects.filter(username=username).exists():
			if len(username) > 5:
				if not User.objects.filter(email=email).exists():
					if(re.fullmatch(for_email, email)):
						pat = re.compile(reg)
						mat = re.search(pat, password)
						if mat:
							user = User.objects.create_user(
								username=username, password=password, email=email)
							user.save()
							data = Profile(username=user)
							data.save()
							temp_obj = User.objects.get(username=username)                                                           
							pro_obj = Profile.objects.get(username=temp_obj)
							serializer_class = RegistrationSerializer(pro_obj)
							result["value"] = True
							result["message"]='success'
							result["data"] = serializer_class.data
							return Response(result, status=status.HTTP_200_OK)
						else:
							result["value"] = False
							result["message"] = "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."
							result['data']=None
							return Response(result, status=status.HTTP_200_OK)
					else:
						result["value"] = False
						result['data']=None
						result["message"] = "Enter valid email address"
      					# result['data']=None
						return Response(result, status=status.HTTP_200_OK)
				else:
					result["value"] = False
					result["message"] = "User Already Exist with this email address"
					result['data']=None
					return Response(result, status=status.HTTP_200_OK)
			else:
				result["value"] = False
				result["message"] = "Username length must be greater than 6"
				result['data']=None
				return Response(result, status=status.HTTP_200_OK)
		else:
			result["value"] = False
			result['data']=None
			result["message"] = "User Already Exists!!!"
			return Response(result, status=status.HTTP_200_OK)

# add tag
@api_view(['POST'])
def tag(request):
	result = dict()
	try:
		header_token = request.META['HTTP_AUTHORIZATION'].split(" ")[1]

		if request.method == "POST":
			tag = request.POST['tag']
			try:
				user_obj = User.objects.get(auth_token__contains = "{" + header_token + "}")
				try:
					tag_obj = Tag.objects.get(username=user_obj)
					tag_obj.tag = tag
					tag_obj.save()
					result["value"] = True
					result["message"] = "Tag/Tags Updated."
					result['data']=None
					return Response(result, status=status.HTTP_200_OK)
				except:
					tag_obj = Tag.objects.create(username=request.user, tag=tag)
					result['data']=None
					result["value"] = True
					result["message"] = "Tag/Tags Added."
					return Response(result, status=status.HTTP_200_OK)
			except Exception as e:
				result["value"] = False
				result["message"] = "User not found"
				result['data']=None
				return Response(result, status=status.HTTP_200_OK)
	except KeyError:
		result["value"] = False
		result["message"] = "Please enter auth token!"
		result['data']=None
		return Response(result, status=status.HTTP_200_OK)				

# application data no auth api
@api_view(['POST'])
def AppDataNoAuth(request):
	result = dict()
	if request.method == "POST":
		UID = request.POST['UID']
		inApp_Products = request.POST.get('inApp_Products')
		Purchase_date = request.POST.get('Purchase_date')
		Purchased_product = request.POST.get('Purchased_product')
		Device_Model = request.POST.get('Device_Model')
		operating_system = request.POST.get('operating_system')
		Device_Storage = request.POST.get('Device_Storage')
		Lunch_count = request.POST.get('Lunch_count')
		Push_Notification_Status = request.POST.get('Push_Notification_Status')
		Library_permission_Status = request.POST.get('Library_permission_Status')
		latitude = request.POST.get('latitude')
		longitude = request.POST.get('longitude')
		Carrier = request.POST.get('Carrier')
		App_Last_Opened = request.POST.get('App_Last_Opened')
		Purchase_attempts = request.POST.get('Purchase_attempts')
		Grace_Period = request.POST.get('Grace_Period')
		Remaining_grace_period_days = request.POST.get('Remaining_grace_period_days')
		Number_of_projects = request.POST.get('Number_of_projects')
		Total_time_spent = request.POST.get('Total_time_spent')
		total_ads_served = request.POST.get('total_ads_served')
		Registered_user = request.POST.get('Registered_user')
		Push_Notification_token = request.POST.get('Push_Notification_token')
		
		try:
			if Purchase_date:
				datetime.strptime(Purchase_date, '%Y-%m-%d')
		except ValueError:
			result["value"] = False
			result["message"] = "Purchase_date in incorrect date format. It should be YYYY-MM-DD"
			result['data']=None
			return Response(result, status=status.HTTP_200_OK)

		try:
			if App_Last_Opened:
				datetime.strptime(App_Last_Opened, '%Y-%m-%d')
		except ValueError:
			result["value"] = False
			result["message"] = "App_Last_Opened in incorrect date format. It should be YYYY-MM-DD"
			result['data']=None
			return Response(result, status=status.HTTP_200_OK)

		if application_data.objects.filter(UID = UID).exists():
			app_data_obj = application_data.objects.get(UID=UID)
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
			app_data_obj.no_auth='True'
			app_data_obj.save()
			result["value"] = True
			result["message"] = "Details Updated."
   
			return Response(result, status=status.HTTP_200_OK)

		else:
			data = application_data(
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
									Push_Notification_token=Push_Notification_token
									)
			# data.save()
			result["value"] = True
			result["message"] = "success"
			result['data']=None
			return Response(result, status=status.HTTP_200_OK)
