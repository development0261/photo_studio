from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.loginprocess, name="login"),
    path('logout/', views.logoutprocess, name="logout"),


    path('AdminUsers/', views.admin_user, name="adminusers"),
    path('AppUsers/', views.app_user, name="custom_user"),
    path('DeleteUser/<str:para>', views.delete_user, name="delete_user"),

    path('Profile/', views.profile_model, name="Profile"),
    path('Profile/<str:info>', views.view_profile, name="view_profile"),
    path('DeleteProfile/<str:para>', views.delete_profile, name="delete_profile"),

    path('user_preference/', views.user_preference_model, name="user_preference"),
    path('user_preference/<str:info>', views.view_user_preference, name="view_user_preference"),
    path('DeleteDetails/<str:para>', views.delete_details, name="delete_details"),

    path('application_data/', views.app_data_model, name="application_data"),
    path('application_data/<str:info>', views.view_app_data, name="view_app_data"),
    path('DeleteAppData/<str:para>', views.delete_app_data, name="delete_app_data"),

    path('Purchase/', views.purchase_model, name="Purchase"),
    path('Purchase/<str:info>', views.view_purchases, name="view_purchases"),
    path('specific_purchase/<str:info>', views.view_purchase, name="view_purchase"),
    path('DeletePurchase/<str:para>', views.delete_purchase, name="delete_purchase"),
    
    path('Tag/', views.tag_model, name="Tag"),
    path('Tag/<str:info>', views.view_tag, name="view_tag"),
    path('DeleteTag/<str:para>', views.delete_tag, name="delete_tag"),

    path('Product/', views.product_model, name="Product"),
    path('Product/<str:info>', views.view_product, name="view_product"),
    path('specific_product/<str:info>', views.specific_product, name="specific_product"),
    path('DeleteProduct/<str:para>', views.delete_product, name="delete_product"),

    path('UserEdit/<str:para>', views.user_edit, name="user_edit"),
    path('AdminEdit/<str:para>', views.admin_edit, name="admin_edit"),
    path('ProfileEdit/<str:para>', views.profile_edit, name="profile_edit"),
    path('PreferencesEdit/<str:para>', views.preferences_edit, name="preferences_edit"),
    path('EditAppData/<str:para>', views.app_data_edit, name="app_data_edit"),
    path('EditPurchase/<str:para>', views.purchase_edit, name="purchase_edit"),
    path('EditTag/<str:para>', views.tag_edit, name="tag_edit"),
    path('EditProduct/<str:para>', views.product_edit, name="product_edit"),

    path('change_password/', views.change_password, name="change_password"),
    path('send_link/', views.send_link, name="send_link"),
    path('forgot_password/<str:token>', views.forgot_password, name="forgot_password"),
    path('export_excel',views.export_excel,name="export_excel")
]