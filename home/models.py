from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class custom_user(AbstractUser):
    confirm_token = models.CharField(null=True, max_length=50)


class Profile(models.Model):
    uid = models.AutoField(primary_key=True, auto_created=True)
    username = models.OneToOneField(custom_user, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    mobile = PhoneNumberField(unique=True)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(max_length=7, choices=GENDER_CHOICES)
    profile_image = models.ImageField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    pass_update = models.DateTimeField(blank=True, null=True)
    pass_forgot = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    dob = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=20, null=True)
    country = models.CharField(max_length=20, null=True)
    lat = models.FloatField(max_length=30, null=True)
    long = models.FloatField(max_length=30, null=True)
    snap = models.CharField(max_length=30, null=True)
    fb = models.CharField(max_length=30, null=True)
    insta = models.CharField(max_length=30, null=True)
    website = models.CharField(max_length=100, null=True)
    avatar = models.ImageField(null=True)
    bitmoji = models.ImageField(null=True)


class user_detail(models.Model):
    udid = models.AutoField(primary_key=True, auto_created=True)
    username = models.OneToOneField(custom_user, on_delete=models.CASCADE)
    signature = models.ImageField(null=True)
    quality_choices = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    )
    export_quality = models.CharField(
        max_length=7, choices=quality_choices)  # (list) high, medium, low
    Language = models.CharField(max_length=20)  # (string)
    user_stared_templates = ArrayField(
        models.CharField(max_length=50), blank=True)  # (array)
    user_stared_backgrounds = ArrayField(
        models.CharField(max_length=50), blank=True)  # (array)
    user_stared_stickers = ArrayField(
        models.CharField(max_length=50), blank=True)  # (array)
    user_stared_Textart = ArrayField(
        models.CharField(max_length=50), blank=True)  # (array)
    user_stared_colors = ArrayField(
        models.CharField(max_length=50), blank=True)  # (array)
    user_stared_fonts = ArrayField(models.CharField(
        max_length=50), blank=True)  # (array)
    most_used_fonts = ArrayField(models.CharField(
        max_length=50), blank=True)  # (array)
    user_custom_colors = ArrayField(
        models.CharField(max_length=50), blank=True)  # (array)
    instagram_follower = models.BooleanField(default=False)  # (boolean)
    grid_snapping = models.BooleanField(default=False)  # (boolean)
    user_recent_text = models.CharField(max_length=255)  # (string)
    appearance_choices = (
        ('Light', 'Light'),
        ('Dark', 'Dark'),
        ('Auto', 'Auto'),
    )
    appearance_mode = models.CharField(
        max_length=7, choices=appearance_choices)  # (list): dark, light, auto
    enable_iCloud_backup = models.BooleanField(default=False)  # (boolean)
    save_projects_automatically = models.BooleanField(
        default=False)  # (boolean)
    save_projects_on_export = models.BooleanField(default=False)  # (boolean)
    notifications_permission = models.BooleanField(default=False)  # (boolean)
    inApp_notifications_permission = models.BooleanField(
        default=False)  # (boolean)
    photo_library_permission = models.BooleanField(default=False)  # (boolean)
    digital_riyals_rewards = models.IntegerField()  # (Number)
    enable_touch = models.BooleanField(default=False)  # (boolean)
    app_choices = (
        ('Option1', 'Option1'),
        ('Option2', 'Option2'),
        ('Option3', 'Option3'),
    )
    app_theme = models.CharField(max_length=7, choices=app_choices)  # (list)
    always_crop = models.BooleanField(default=False)  # (boolean)


class application_data(models.Model):
    aid = models.AutoField(primary_key=True, auto_created=True)
    UID = models.CharField(unique=True, max_length=200)
    username = models.OneToOneField(custom_user, on_delete=models.CASCADE)
    inApp_Products = models.CharField(max_length=100)
    Purchase_date = models.DateTimeField(blank=True, null=True)
    Purchased_product = models.CharField(max_length=100)
    Device_Model = models.CharField(max_length=50)
    iOS = models.CharField(max_length=100)
    Device_Storage = models.CharField(max_length=10)
    Lunch_count = models.IntegerField()
    Push_Notification_Status = models.BooleanField(default=False)
    Library_permission_Status = models.BooleanField(default=False)
    Latest_Geolocation = models.FloatField(max_length=30)
    Carrier = models.CharField(max_length=100)
    App_Last_Opened = models.DateTimeField()
    Purchase_attempts = models.IntegerField()
    Grace_Period = models.CharField(max_length=100)
    Remaining_grace_period_days = models.IntegerField()
    Number_of_projects = models.IntegerField()
    Total_time_spent = models.CharField(max_length=10)
    total_ads_served = models.IntegerField()
    Registered_user = models.BooleanField(default=False)
    Push_Notification_token = models.BooleanField(default=False)
