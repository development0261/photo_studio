from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('User/', views.user_model, name="custom_user"),
    # path('get_data/<str:info>', views.get_data, name="get_data"),
    path('Profile/', views.profile_model, name="Profile"),
    path('Profile/<str:info>', views.view_profile, name="view_profile"),
    path('user_detail/', views.user_deatils_model, name="user_detail"),
    path('user_detail/<str:info>', views.view_user_detail, name="view_user_detail"),
    path('application_data/', views.app_data_model, name="application_data"),
    path('application_data/<str:info>', views.view_app_data, name="view_app_data"),
    path('Purchase/', views.purchase_model, name="Purchase"),
    path('Purchase/<str:info>', views.view_purchase, name="view_purchase"),
    path('Tag/', views.tag_model, name="Tag"),
    path('Tag/<str:info>', views.view_tag, name="view_tag"),
    path('Product/', views.product_model, name="Product"),
    path('Product/<str:info>', views.view_product, name="view_product"),


]