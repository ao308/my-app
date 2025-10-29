from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('regist', views.regist, name='regist'),
    path('login' , views.user_login, name='user_login'),
    path('logout' , views.user_login, name='user_logout'),
    path('home', views.home_view, name='home')
]