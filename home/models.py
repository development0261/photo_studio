from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
# Create your models here.

from django.contrib.auth.models import User
User._meta.get_field('email')._unique = True

class custom_user(AbstractUser):
    delete_date = models.DateTimeField(null=True, blank=True)
    confirm_token = models.CharField(null=True, blank=True, max_length=50)
    social_token = models.TextField(null=True, blank=True)
    social_registration = models.CharField(max_length=255, null=True, blank=True)
    social_account = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "custom_user"
        unique_together = ('email',)


class Profile(models.Model):
    uid = models.AutoField(primary_key=True, auto_created=True)
    username = models.OneToOneField(custom_user, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    # email = models.CharField(max_length=50, null=True, blank=True, unique=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(
        max_length=7, choices=GENDER_CHOICES, null=True, blank=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to='')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    pass_update = models.DateField(blank=True, null=True)
    pass_forgot = models.DateField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    lat = models.FloatField(max_length=30, null=True, blank=True)
    long = models.FloatField(max_length=30, null=True, blank=True)
    snap = models.CharField(max_length=30, null=True, blank=True)
    fb = models.CharField(max_length=30, null=True, blank=True)
    insta = models.CharField(max_length=30, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True)
    bitmoji = models.ImageField(null=True, blank=True)
    delete_account = models.BooleanField(default=False)
    expiration_date = models.DateTimeField(null=True, blank=True)
    count_for_forgot_pass = models.PositiveSmallIntegerField(default=0)
    time_for_forgot_pass = models.DateTimeField(null=True, blank=True)
    isSocial = models.BooleanField(default=False)
    country_code = models.CharField(max_length=30,null=True, blank=True,default=None)

    def __str__(self):
        return f"{self.username} - {self.name}"

    class Meta:
        verbose_name_plural = "Profile"


class user_preference(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.udid}"

    class Meta:
        verbose_name_plural = "user_preference"


class application_data(models.Model):
    aid = models.AutoField(primary_key=True, auto_created=True)
    UID = models.CharField(unique=True, max_length=200)
    username = models.ForeignKey(custom_user, on_delete=models.CASCADE)
    inApp_Products = models.CharField(max_length=100)
    Purchase_date = models.DateTimeField(blank=True, null=True)
    Purchased_product = models.CharField(max_length=100)
    Device_Model = models.CharField(max_length=50)
    operating_system = models.CharField(max_length=100)
    Device_Storage = models.CharField(max_length=10)
    Lunch_count = models.IntegerField()
    Push_Notification_Status = models.BooleanField(default=False)
    Library_permission_Status = models.BooleanField(default=False)
    latitude = models.FloatField(blank=True, null=True,max_length=30)
    longitude = models.FloatField(blank=True, null=True,max_length=30)
    Carrier = models.CharField(max_length=100)
    App_Last_Opened = models.DateTimeField(blank=True, null=True)
    Purchase_attempts = models.IntegerField()
    Grace_Period = models.CharField(max_length=100)
    Remaining_grace_period_days = models.IntegerField()
    Number_of_projects = models.IntegerField()
    Total_time_spent = models.CharField(max_length=10)
    total_ads_served = models.IntegerField()
    Registered_user = models.BooleanField(default=False)
    Push_Notification_token = models.CharField(
        max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.UID}"

    class Meta:
        verbose_name_plural = "Application data"


class Product(models.Model):
    PID = models.AutoField(primary_key=True, auto_created=True)
    productID = models.CharField(max_length=255, unique=True)
    product = models.CharField(max_length=255, unique=True)
    productPromo = models.CharField(max_length=255, null=True, blank=True)
    promoPrice = models.FloatField(max_length=255, null=True, blank=True)
    annaulSubProd = models.CharField(max_length=255, null=True, blank=True)
    annaulSub = models.CharField(max_length=255, null=True, blank=True)
    monthlySubProd = models.CharField(max_length=255, null=True, blank=True)
    monthlySub = models.CharField(max_length=255, null=True, blank=True)
    localeId = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.product}"

    class Meta:
        verbose_name_plural = "Product"


class Purchase(models.Model):
    pid = models.AutoField(primary_key=True, auto_created=True)
    username = models.ForeignKey(custom_user, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    pstatus = models.CharField(max_length=20)
    auto_renew_status = models.BooleanField(default=False)
    is_in_billing_retry_period = models.BooleanField(default=False)
    is_in_intro_offer_period = models.BooleanField(default=False)
    is_trial_period = models.BooleanField(default=False)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    subscription_type = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.pstatus}"

    class Meta:
        verbose_name_plural = "Purchase"


class Tag(models.Model):
    username = models.OneToOneField(custom_user, on_delete=models.CASCADE)
    tag = ArrayField(models.CharField(max_length=50), null=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.tag}"

    class Meta:
        verbose_name_plural = "Tag"


class application_data_noauth(models.Model):
    aid = models.AutoField(primary_key=True, auto_created=True)
    UID = models.CharField(unique=True, max_length=200)
    # username = models.ForeignKey(custom_user, on_delete=models.CASCADE)
    inApp_Products = models.CharField(max_length=100)
    Purchase_date = models.DateTimeField(blank=True, null=True)
    Purchased_product = models.CharField(max_length=100)
    Device_Model = models.CharField(max_length=50)
    operating_system = models.CharField(max_length=100)
    Device_Storage = models.CharField(max_length=10)
    Lunch_count = models.IntegerField()
    Push_Notification_Status = models.BooleanField(default=False)
    Library_permission_Status = models.BooleanField(default=False)
    latitude = models.FloatField(blank=True, null=True,max_length=30)
    longitude = models.FloatField(blank=True, null=True,max_length=30)
    Carrier = models.CharField(max_length=100)
    App_Last_Opened = models.DateTimeField(blank=True, null=True)
    Purchase_attempts = models.IntegerField()
    Grace_Period = models.CharField(max_length=100)
    Remaining_grace_period_days = models.IntegerField()
    Number_of_projects = models.IntegerField()
    Total_time_spent = models.CharField(max_length=10)
    total_ads_served = models.IntegerField()
    Registered_user = models.BooleanField(default=False)
    Push_Notification_token = models.CharField(
        max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.UID}"

    class Meta:
        verbose_name_plural = "Application data no auth"

