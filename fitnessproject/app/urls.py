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
    path("exercise/new/", views.exercise_new, name="exercise_new"),
    path('exercise/edit/<int:pk>/', views.exercise_edit, name='exercise_edit'),
    path('exercise/record/', views.exercise_record, name='exercise_record'),
    path('exercise/record/edit/', views.exercise_record_edit, name='exercise_record_edit'),
    path('exercise/delete/<int:pk>/', views.exercise_delete, name='exercise_delete'),
    path("record/delete/<int:pk>/", views.record_delete, name="record_delete"),
    path('favorite', FavoriteView.as_view(), name='favorite'),
    path("exercise/favorite/toggle/<int:pk>/", views.toggle_favorite, name="toggle_favorite"),
    path('mypage', MypageView.as_view(), name='mypage'),
]