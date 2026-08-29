from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('app:home')),
    path('fitnessproject/', include('app.urls')),
    path('admin/', admin.site.urls),
]
