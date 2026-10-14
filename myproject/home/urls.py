from django.contrib import admin
from django.urls import path, include

# home/urls.py (APP level)
from django.urls import path
from . import views  # This is CORRECT here!

urlpatterns = [
    path('', views.home_page, name='home'),
    path('accounts/ajax-login/', views.ajax_login, name='ajax_login'),
    path('accounts/ajax-signup/', views.ajax_signup, name='ajax_signup'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/save-health-profile/', views.save_health_profile, name='save_health_profile'),
    path('accounts/ajax-save-product/', views.ajax_save_product, name='ajax_save_product'),
    path('accounts/diet-plan/', views.get_diet_plan, name='diet_plan'),
    path('accounts/ajax-alternatives/', views.ajax_alternatives, name='ajax_alternatives'),
    path('scan/', views.scan_barcode_and_get_food, name='scan_barcode'),
    path('get-profile/', views.get_profile, name='get_profile'),
    path("get-history/", views.get_user_history, name="get_history"),


]