from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, Purchase
from django.contrib.auth import get_user_model

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username','email', 'name', 'isAdmin']

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
            "social_media_site":register.username.social_media_site,
            "social_id":register.username.social_id
        }
    class Meta:
        model = Profile
        exclude = ['username']

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True,source="username")
    def get_user(self, register):
        return {
            "first_name":register.username.first_name,
            "last_name":register.username.last_name,
            "email":register.username.email,
            "username":register.username.username,
            "social_media_site":register.username.social_media_site,
            "password":register.username.password,
            "social_id":register.username.social_id
        }
    class Meta:
        model = Profile
        exclude = ['username']
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        latest_purchase = Purchase.objects.filter(username = instance.username).last()
        if latest_purchase:
            response['InAppPurchaseHistory'] = PurchaseSerializer(latest_purchase,many=False).data
        else:
            response['InAppPurchaseHistory'] = "Didn't purchase anything yet."
        return response    

class SocialSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True,source="username")
    def get_user(self, register):
        return {
            "first_name":register.username.first_name,
            "last_name":register.username.last_name,
            "token":register.username.token,
            "email":register.username.email,
            "username":register.username.username,
            "social_media_site":register.username.social_media_site,
            "social_id":register.username.social_id
        }
    class Meta:
        model = Profile
        exclude = ['username']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj.username)
        return str(token.access_token)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        latest_purchase = Purchase.objects.filter(username = instance.username).last()
        if latest_purchase:
            response['InAppPurchaseHistory'] = PurchaseSerializer(latest_purchase,many=False).data
        else:
            response['InAppPurchaseHistory'] = "Didn't purchase anything yet."
        return response