from django.urls import path
from . import views

urlpatterns = [
    
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('social_media_registration/', views.social_media_registration, name='social_media_registration'),
    path('user_count/', views.user_count, name='user_count'),
    path('genderwise/', views.genderwise, name='genderwise'),
    path('countrywise/', views.countrywise, name='countrywise'),
    path('preferences/', views.preferences, name='preferences'),
    path('delete/', views.delete_account, name='delete'),
    path('specific_user/', views.specific_user, name='specific_user'),
    path('email_verification/', views.email_verification, name='email_verification'),
    path('username_verification/', views.username_verification, name='username_verification'),
    path('app_data/', views.app_data, name='app_data'),  
    path('send_link/', views.send_link, name='send_link'),
    path('forgot_password/<str:t>', views.forgot_password, name="forgot_password"),
    path('update_password/', views.update_password, name="update_password"),
    path('logout/', views.logoutProcess, name='logout'),
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    path('product/', views.product, name='product'),


]

