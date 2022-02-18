from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('User/', views.user_model, name="custom_user"),
    path('Profile/', views.profile_model, name="Profile"),
    path('Profile/<str:info>', views.view_profile, name="view_profile"),
    path('user_detail/', views.user_deatils_model, name="user_detail"),
    path('application_data/', views.app_data_model, name="application_data"),
    path('Purchase/', views.purchase_model, name="Purchase"),
    path('Tag/', views.tag_model, name="Tag"),
    path('Product/', views.product_model, name="Product"),

]