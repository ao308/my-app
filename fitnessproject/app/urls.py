from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login' , views.user_login, name='login'),
    path('home', views.home_view, name='home'),
]