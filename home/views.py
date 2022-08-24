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
from datetime import datetime, timedelta
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

#get city and country
from geopy.geocoders import Nominatim
from pycountry import countries


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
users_obj = User.objects.filter(is_active=False)
for row in users_obj:
	if row.delete_date + timedelta(days=30):
		users_obj.delete()
		
def main_index(request):
	return render(request,"main_index.html")

# for login
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		result = dict()
		if User.objects.filter(username=attrs['username']).exists():
			if not check_password(attrs['password'], User.objects.get(username=attrs['username']).password):
				result["value"] = False
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

				del data['refresh']
				del data['access']
				result["value"] = True
				result["data"] = data
				return result
		else:
			result["value"] = False
			result["message"] = "Account with this username is not exists"
			return result

class MyTokenObtainPairView(TokenObtainPairView):
	serializer_class = MyTokenObtainPairSerializer

# for logout
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logoutProcess(request):
	result = dict()
	logout(request)
	result["value"] = False
	result["data"] = "Successfully Logged Out"
	return Response(result, status=status.HTTP_200_OK)

# user registration
@api_view(['POST'])
def register(request):
	result = dict()
	if request.method == "POST":
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		name = request.POST['name']
		mobile = request.POST.get('mobile')
		gender = request.POST['gender']
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
									result["data"] = final_data

									headers = {
										'Content-Type': 'application/json'
									}

									return Response(result, headers=headers, status=status.HTTP_200_OK)
								else:
									result["value"] = False
									result["message"] = "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."
									return Response(result, status=status.HTTP_400_BAD_REQUEST)
							else:
								result["value"] = False
								result["message"] = "Enter valid email address"
								return Response(result, status=status.HTTP_400_BAD_REQUEST)
						else:
							result["value"] = False
							result["message"] = "Phone number already registered"
							return Response(result, status=status.HTTP_400_BAD_REQUEST)
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
								result["value"] = True
								result["data"] = final_data
								return Response(result, status=status.HTTP_200_OK)
							else:
								result["value"] = False
								result["message"] = "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."
								return Response(result, status=status.HTTP_400_BAD_REQUEST)
						else:
							result["value"] = False
							result["message"] = "Enter valid email address!!!"
							return Response(result, status=status.HTTP_400_BAD_REQUEST)
				else:
					result["value"] = False
					result["message"] = "User Already Exist with this email address!!!"
					return Response(result, status=status.HTTP_400_BAD_REQUEST)
			else:
				result["value"] = False
				result["message"] = "Username length must be greater than 6!!!"
				return Response(result, status=status.HTTP_400_BAD_REQUEST)
		else:
			result["value"] = False
			result["message"] = "User Already Exists!!!"
			return Response(result, status=status.HTTP_400_BAD_REQUEST)

# user registration using social media
@api_view(['POST'])
def social_media_registration(request):
	try:
		result = dict()
		if request.method == "POST":
			social_token = request.POST['social_token']
			social_registration = request.POST['social_registration']
			social_account = request.POST['social_account']

			if 'profile_image' in request.FILES:
				profile_image = request.FILES['profile_image']

			if 'email' in request.POST:
				email = request.POST['email']

			first_name = request.POST.get('first_name')
			last_name = request.POST.get('last_name')

			if social_token:
				if not User.objects.filter(social_token=social_token).exists():
					try:
						user = User.objects.create_user(
							username=social_token, password=social_token, email=email,
							social_token=social_token, social_registration=social_registration, social_account=social_account,first_name=first_name,last_name=last_name)
						user.save()

						profile_obj = Profile(username=user)
						if 'profile_image' in request.FILES:
							profile_obj.profile_image = profile_image
						profile_obj.save()
						serializer_class = SocialSerializer(profile_obj)
						result["value"] = True
						result["data"] = serializer_class.data
						return Response(result, status=status.HTTP_200_OK)
					except IntegrityError:
						result["value"] = False
						result["message"] = "Email already Used!"
						return Response(result,status=status.HTTP_400_BAD_REQUEST)
				else:
					user_obj = User.objects.get(social_token=social_token)
					profile_obj = Profile.objects.get(username=user_obj)
					serializer_class = SocialSerializer(profile_obj)
					result["value"] = True
					result["data"] = serializer_class.data
					return Response(result, status=status.HTTP_200_OK)
	except Exception:
		result["value"] = False
		result["message"] = "Something went wrong! Please contact to support team."
		return Response(result,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
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
					result["data"] = data
					return Response(result, status=status.HTTP_401_UNAUTHORIZED)
				else:
					result["value"] = False
					result["message"] = "You have too many attempts in an Hour!!!You can try after an Hour."
					return Response(result)
		else:
			result["value"] = False
			result["message"] = "User Not Exist with this email address"
			return Response(result,status=status.HTTP_401_UNAUTHORIZED)

# reset-password 
@api_view(['GET'])
def reset_password(request):
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
											result["message"] =  "Password updated Successfully."
											return Response(result, status=status.HTTP_200_OK)
										else:
											result["value"] = False
											result["message"] = "New password and confirm password doesnot matched."
											return Response(result, status=status.HTTP_400_BAD_REQUEST)
									else:
										result["value"] = False
										result["message"] = "Password must be include atleast one special character,number,small and capital letter and length between 6 to 20."
										return Response(result, status=status.HTTP_400_BAD_REQUEST)
								else:
									result["value"] = False
									result["message"] = "Oops!! Please check your Token"
									return Response(result, status=status.HTTP_401_UNAUTHORIZED)
							else:
								result["value"] = False
								result["message"] = "User Not Exist with this email address"
								return Response(result, status=status.HTTP_401_UNAUTHORIZED)
						else:
							result["value"] = False
							result["message"] = "Oops! Your Token is Expired!!!"
							return Response(result, status=status.HTTP_400_BAD_REQUEST)
					else:
						result["value"] = False
						result["message"] = "Please check your Token!!!"
						return Response(result, status=status.HTTP_401_UNAUTHORIZED)
				else:
					result["value"] = False
					result["message"] = "You have changed your password once through your this token!"
					return Response(result, status=status.HTTP_400_BAD_REQUEST)
			else:
				result["value"] = False
				result["message"] = "Please check your Token!!!"
				return Response(result, status=status.HTTP_401_UNAUTHORIZED)
		except:
			result["value"] = False
			result["message"] = "User Not Exist with this email address"
			return Response(result, status=status.HTTP_401_UNAUTHORIZED)
	else:
		result["value"] = False
		result["message"] = "Method Not Allowed!!!"
		return Response(result, status=status.HTTP_405_METHOD_NOT_ALLOWED)
				
# update-password
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
	result = dict()
	if request.method == "POST":
		password = request.POST['password']
		new_pass = request.POST['new_pass']
		confirm_pass = request.POST['confirm_pass']
		if password == new_pass:
			result["value"] = False
			result["message"] = "Old Password and New Password must be diffrent"
			return Response(result, status=status.HTTP_400_BAD_REQUEST)
		if User.objects.filter(username=request.user).exists():
			user = authenticate(username=request.user, password=password)
			if user:
				pat = re.compile(reg)
				mat = re.search(pat, new_pass)
				if mat:
					if new_pass == confirm_pass:
						obj1 = User.objects.get(username=request.user)
						obj1.set_password(new_pass)
						obj2 = User.objects.get(
							username=request.user).profile
						obj2.pass_update = datetime.now()
						obj1.save()
						obj2.save()
						result["value"] = True

						serializer_class = UserSerializerWithToken(obj1)
						result["access-token"] = serializer_class.data
						
						result["message"] = "Password updated Successfully."
						
						return Response(result, status=status.HTTP_200_OK)
					else:
						result["value"] = False
						result["message"] = "New password and confirm password doesnot matched."
						return Response(result, status=status.HTTP_400_BAD_REQUEST)
				else:
					result["value"] = False
					result["message"] = "Password must be include atleast one special character,number,small and capital letter and length between 6 to 20."
					return Response(result, status=status.HTTP_400_BAD_REQUEST)
			else:
				result["value"] = False
				result["message"] = "Password Not matched!!!"
				return Response(result, status=status.HTTP_401_UNAUTHORIZED)
		else:
			result["value"] = False
			result["message"] = "User Not Exist with this username"
			return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# edit profile
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def profile(request, para=None):
	result = dict()
	if request.method == "POST":
		email = request.POST.get('email')
		name = request.POST.get('name')
		mobile = request.POST.get('mobile')
		gender = request.POST.get('gender')
		date_of_Birth = request.POST.get('dob')
		city = request.POST.get('city')
		country = request.POST.get('country')
		user_Latitude = request.POST.get('lat')
		user_Longitude = request.POST.get('long')
		snapchat = request.POST.get('snap')
		facebook = request.POST.get('fb')
		instagram = request.POST.get('insta')
		website = request.POST.get('website')
		# country_code = request.POST.get('country_code')
		# g = geocoder.osm([user_Latitude,user_Longitude], method='reverse')
		country_code = None
		if user_Latitude and user_Longitude:
			location = geolocator.reverse(user_Latitude+","+user_Longitude)
			address = location.raw['address']
			country = address.get('country', '')
			country_code = countries.get(name=country).alpha_2
		try:
			if date_of_Birth in request.POST:
				datetime.strptime(date_of_Birth, '%Y-%m-%d')
		except ValueError:
			result["value"] = False
			result["message"] = "date_of_Birth in incorrect date format. It should be YYYY-MM-DD"
			return Response(result, status=status.HTTP_400_BAD_REQUEST)

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
		
		try:
			user_obj = User.objects.get(username=request.user)
			if user_obj.email != email:
				if User.objects.filter(email=email):
					return Response({"Error": "Email already in use!!!"}, status=status.HTTP_400_BAD_REQUEST)
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
			if country_code:
				profile_obj.country_code = country_code
			else:
				profile_obj.country_code = None
			profile_obj.save()
			user_obj.save()
			result["value"] = True
			result["message"] = "Profile Updated"
			return Response(result, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			result["value"] = False
			result["message"] = "User Not Exist!!!"
			return Response(result, status=status.HTTP_401_UNAUTHORIZED)
			
# get specific user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def specific_user(request):
	result = dict()
	if request.method == "GET":
		queryset = Profile.objects.filter(username__username=request.user)
		serializer_class = ProfileSerializer(queryset, many=True)
		result['value']= True
		result['data'] = serializer_class.data[0]
		return Response(result, status=status.HTTP_200_OK)

# get total user
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_count(request):
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer(queryset, many=True)
	return Response({'Total users': len(serializer_class.data)}, status=status.HTTP_200_OK)

# total user with specific gender
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def genderwise(request):
	gen = request.GET['gender']
	obj1 = Profile.objects.filter(gender__iexact=gen)
	serializer_class = ProfileSerializer(obj1, many=True)
	return Response({f'Total users with {gen} gender': len(serializer_class.data)}, status=status.HTTP_200_OK)

# total user with specific country
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def countrywise(request):
	con = request.GET['country']
	obj1 = Profile.objects.filter(country__iexact=con)
	serializer_class = ProfileSerializer(obj1, many=True)
	return Response({f'Users with {con} country': serializer_class.data}, status=status.HTTP_200_OK)

# add and edit user preferences
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def preferences(request):
	result = dict()
	if request.method == "POST":
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
			user = User.objects.get(username=request.user)
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
					result["value"] = True
					result["message"] = "preferences Added."
					return Response(result, status=status.HTTP_200_OK)
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
				result["value"] = False
				result["message"] = "User preferences updated."
				return Response(result, status=status.HTTP_200_OK)
		except:
			result["value"] = False
			result["message"] = "User not Found!!!"
			return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# add and edit application data
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def app_data(request):
	result = dict()
	if request.method == "POST":
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
		try:
			datetime.strptime(Purchase_date, '%Y-%m-%d')
		except ValueError:
			result["value"] = False
			result["message"] = "Purchase_date in incorrect date format. It should be YYYY-MM-DD"
			return Response(result, status=status.HTTP_400_BAD_REQUEST)

		try:
			datetime.strptime(App_Last_Opened, '%Y-%m-%d')
		except ValueError:
			result["value"] = False
			result["message"] = "App_Last_Opened in incorrect date format. It should be YYYY-MM-DD"
			return Response(result, status=status.HTTP_400_BAD_REQUEST)
		try:
			user = User.objects.get(username=request.user)
			if application_data.objects.filter(username=user).exists():
				if application_data.objects.filter(UID = UID).exists():
					try:
						app_data_obj = application_data.objects.get(username =user, UID = UID)
						# app_data_obj.UID = UID
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
						print(e)
						return Response({"Error": "UID Exists!!!"}, status=status.HTTP_409_CONFLICT)
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
					return Response({"Success": "Details Added."}, status=status.HTTP_200_OK)


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
		except Exception as e:
			print(e)
			return Response({"Error": "User not Found!!!"}, status=status.HTTP_401_UNAUTHORIZED)
			
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
			return Response(result, status=status.HTTP_400_BAD_REQUEST)
		except:
			result["value"] = True
			result["message"]= "Email is available."
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
			return Response(result, status=status.HTTP_400_BAD_REQUEST)
		except:
			result["value"]=True
			result["message"]="Username is available."
			return Response(result, status=status.HTTP_200_OK)

# add and update purchase history
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchase_history(request):
	result = dict()
	if request.method == "POST":
		pstatus = request.POST['pstatus']
		auto_renew_status = request.POST['auto_renew_status']
		is_in_billing_retry_period = request.POST['is_in_billing_retry_period']
		is_in_intro_offer_period = request.POST['is_in_intro_offer_period']
		is_trial_period = request.POST['is_trial_period']
		start_date = request.POST['start_date']
		end_date = request.POST['end_date'] 
		subscription_type = request.POST['subscription_type']
		try:
			datetime.strptime(start_date, '%Y-%m-%d')
		except ValueError:
			result["value"]=False
			result["message"]="start_date in incorrect date format. It should be YYYY-MM-DD"
			return Response(result, status=status.HTTP_400_BAD_REQUEST)		
		try:
			datetime.strptime(end_date, '%Y-%m-%d')
		except ValueError:
			result["value"]=False
			result["message"]="end_date in incorrect date format. It should be YYYY-MM-DD"
			return Response(result, status=status.HTTP_400_BAD_REQUEST)
		
		try:
			user = User.objects.get(username=request.user)
			try:
				purchase_obj = Purchase.objects.get(username=user.id)
				purchase_obj.pstatus = pstatus
				purchase_obj.auto_renew_status = auto_renew_status
				purchase_obj.is_in_billing_retry_period = is_in_billing_retry_period
				purchase_obj.is_in_intro_offer_period = is_in_intro_offer_period
				purchase_obj.is_trial_period = is_trial_period
				purchase_obj.start_date = start_date
				purchase_obj.end_date = end_date
				purchase_obj.subscription_type = subscription_type
				purchase_obj.save()
				result["value"]=True
				result["message"]= "Data Updated"
				return Response(result, status=status.HTTP_200_OK)
			except Exception as e:
				obj = Purchase(
					username=user,
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
				return Response(result, status=status.HTTP_200_OK)
		except Exception as e:
			result["value"]=False
			result["message"]="User Not Exist!!!"
			return Response(result, status=status.HTTP_401_UNAUTHORIZED)


# delete account
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
	result = dict()
	if request.method == "POST":
		try:
			user_obj = User.objects.get(username=request.user)
			user_obj.is_active = False
			user_obj.delete_date = datetime.now()
			user_obj.save()
			result["value"] = True
			result["message"] = "Your account is under deleting process and deleted in 30 days."
			return Response(result, status=status.HTTP_200_OK)
		except Exception as e:
			result["value"] = False
			result["message"] = "User not found"
			return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# add and update products
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def product(request):
	result = dict()
	if request.method == "POST":
		productID = request.POST['productID']
		product = request.POST['product']
		productPromo = request.POST['productPromo']
		promoPrice = request.POST['promoPrice']
		annaulSubProd = request.POST['annaulSubProd']
		annaulSub = request.POST['annaulSub']
		monthlySubProd = request.POST['monthlySubProd']
		monthlySub = request.POST['monthlySub']
		localeId = request.POST['localeId']

		try:
			user_obj = User.objects.get(username=request.user)
			try:
				product1 = Product.objects.get(product=product)
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
				product1 = Product.objects.create(
					# username=user_obj,
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
		except Exception as e:
			result["value"] = False
			result["message"] = "User not found"
			return Response(result, status=status.HTTP_401_UNAUTHORIZED)


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
							result["message"] = serializer_class.data
							return Response(result, status=status.HTTP_200_OK)
						else:
							result["value"] = False
							result["message"] = "password must be include atleast one special character,number,small and capital letter and length between 6 to 20."
							return Response(result, status=status.HTTP_400_BAD_REQUEST)
					else:
						result["value"] = False
						result["message"] = "Enter valid email address"
						return Response(result, status=status.HTTP_400_BAD_REQUEST)
				else:
					result["value"] = False
					result["message"] = "User Already Exist with this email address"
					return Response(result, status=status.HTTP_400_BAD_REQUEST)
			else:
				result["value"] = False
				result["message"] = "Username length must be greater than 6"
				return Response(result, status=status.HTTP_400_BAD_REQUEST)
		else:
			result["value"] = False
			result["message"] = "User Already Exists!!!"
			return Response(result, status=status.HTTP_400_BAD_REQUEST)


# add tag
@api_view(['POST'])
def tag(request):
	result = dict()
	if request.method == "POST":
		tag = request.POST['tag']
		try:
			user_obj = User.objects.get(username=request.user)
			try:
				tag_obj = Tag.objects.get(username=user_obj)
				tag_obj.tag = tag
				tag_obj.save()
				result["value"] = True
				result["message"] = "Tag/Tags Updated."
				return Response(result, status=status.HTTP_200_OK)
			except:
				tag_obj = Tag.objects.create(username=request.user, tag=tag)
				result["value"] = True
				result["message"] = "Tag/Tags Added."
				return Response(result, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			result["value"] = False
			result["message"] = "User not found"
			return Response(result, status=status.HTTP_401_UNAUTHORIZED)

# application data no auth api
@api_view(['POST'])
def AppDataNoAuth(request):
	result = dict()
	if request.method == "POST":
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
		try:
			datetime.strptime(Purchase_date, '%Y-%m-%d')
		except ValueError:
			result["value"] = False
			result["message"] = "Purchase_date in incorrect date format. It should be YYYY-MM-DD"
			return Response(result, status=status.HTTP_400_BAD_REQUEST)

		try:
			datetime.strptime(App_Last_Opened, '%Y-%m-%d')
		except ValueError:
			result["value"] = False
			result["message"] = "App_Last_Opened in incorrect date format. It should be YYYY-MM-DD"
			return Response(result, status=status.HTTP_400_BAD_REQUEST)
		try:
			if application_data.objects.filter(UID = UID).exists():
				app_data_obj = application_data_noauth.objects.get(UID=UID)
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
				result["value"] = True
				result["message"] = "Details Updated."
				return Response(result, status=status.HTTP_200_OK)

			else:
				data = application_data_noauth(
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
				data.save()
				result["value"] = True
				result["message"] = "Details Added."
				return Response(result, status=status.HTTP_200_OK)

		except Exception as e:
			print(e)
			result["value"] = False
			result["message"] = "User not Found!!!"
			return Response(result, status=status.HTTP_401_UNAUTHORIZED)
