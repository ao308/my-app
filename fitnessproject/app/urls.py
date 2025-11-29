from django.urls import path
from . views import(
    IndexView, RegistUserView, HomeView, UserLoginView, UserLogoutView, FavoriteView, MypageView,
)
from . import views

app_name = 'app'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('regist', RegistUserView.as_view(), name='regist'),
    path('login' , UserLoginView.as_view(), name='user_login'),
    path('logout' , UserLogoutView.as_view(), name='user_logout'),
    path('home', views.home, name='home'),
    path('objective', views.objective_list, name='objective'),
    path('objective/<int:goal_id>/edit/', views.edit_goal, name='edit_goal'),
    path('objective/create/', views.create_goal, name='create_goal'),
    path('goal/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('goal/<int:goal_id>/complete/', views.complete_goal, name='complete_goal'),
    path('goals/create/', views.create_goal, name='create_goal'),
    path('favorite', FavoriteView.as_view(), name='favorite'),
    path('mypage', MypageView.as_view(), name='mypage'),
]