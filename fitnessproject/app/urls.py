from django.urls import path
from . views import(
    IndexView, RegistUserView, HomeView, UserLoginView, UserLogoutView
)

app_name = 'app'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('regist', RegistUserView.as_view(), name='regist'),
    path('login' , UserLoginView.as_view(), name='user_login'),
    path('logout' , UserLogoutView.as_view(), name='user_logout'),
    path('home', HomeView.as_view(), name='home'),
]