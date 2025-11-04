from django.urls import path
from . views import(
    IndexView, RegistUserView, HomeView, UserLoginView, UserLogoutView, ObjectiveView, FavoriteView, MypageView,
)

app_name = 'app'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('regist', RegistUserView.as_view(), name='regist'),
    path('login' , UserLoginView.as_view(), name='user_login'),
    path('logout' , UserLogoutView.as_view(), name='user_logout'),
    path('home', HomeView.as_view(), name='home'),
    path('objective', ObjectiveView.as_view(), name='objective'),
    path('favorite', FavoriteView.as_view(), name='favorite'),
    path('mypage', MypageView.as_view(), name='mypage'),
]