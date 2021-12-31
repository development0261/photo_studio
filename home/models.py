from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class custom_user(AbstractUser):
    confirm_token = models.CharField(null=True,max_length=50)

class Registration(models.Model):
    uid = models.AutoField(primary_key=True,auto_created = True)
    username = models.OneToOneField(custom_user, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    mobile = PhoneNumberField(unique=True)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(max_length=7, choices=GENDER_CHOICES)
    dob = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    lat = models.FloatField(max_length=30)
    long = models.FloatField(max_length=30)
    snap = models.CharField(max_length=30)
    fb = models.CharField(max_length=30)
    insta = models.CharField(max_length=30)
    profile = models.ImageField(null=True)
    website = models.CharField(max_length=100)
    avatar = models.ImageField(null=True)
    bitmoji = models.ImageField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
