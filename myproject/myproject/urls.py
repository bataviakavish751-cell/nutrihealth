# myproject/urls.py (PROJECT level)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # NO views import here!
]