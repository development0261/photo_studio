from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin']

    def get__id(self, obj):
        return obj.id

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

class RegistrationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True,source="username")
    def get_user(self, register):
        return {
            "first_name":register.username.first_name,
            "last_name":register.username.last_name,
            "email":register.username.email,
            "username":register.username.username,
            "password":register.username.password,
        }
    class Meta:
        model = Profile
        exclude = ['username']

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True,source="username")
    def get_user(self, register):
        return {
            "first_name":register.username.first_name,
            "last_name":register.username.last_name,
            "email":register.username.email,
            "username":register.username.username,
            "password":register.username.password,
        }
    class Meta:
        model = Profile
        exclude = ['username']

class SocialSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True,source="username")
    def get_user(self, register):
        return {
            "first_name":register.username.first_name,
            "last_name":register.username.last_name,
            "social_token":register.username.social_token,
            "social_account":register.username.social_account,
            "social_registration":register.username.social_registration,
            "email":register.username.email,
        }
    class Meta:
        model = Profile
        exclude = ['username']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj.username)
        return str(token.access_token)