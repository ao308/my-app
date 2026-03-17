from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('regist', views.RegistUserView.as_view(), name='regist'),
    path('login', views.UserLoginView.as_view(), name='user_login'),
    path('logout', views.UserLogoutView.as_view(), name='user_logout'),
    path('home', views.home, name='home'),
    path('goal/', views.goal_list, name='goal_list'),
    path('goal/create/', views.create_goal, name='create_goal'),
    path('goal/<int:goal_id>/edit/', views.edit_goal, name='edit_goal'),
    path('goal/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('goal/<int:goal_id>/complete/', views.complete_goal, name='complete_goal'),
    path('goal/<int:goal_id>/undo/', views.undo_complete_goal, name='undo_goal'),
    path("exercise/new/", views.exercise_new, name="exercise_new"),
    path('exercise/edit/<int:pk>/', views.exercise_edit, name='exercise_edit'),
    path('exercise/delete/<int:pk>/', views.exercise_delete, name='exercise_delete'),
    path('exercise/record/', views.exercise_record, name='exercise_record'),
    path('exercise/record/new/', views.exercise_record_new, name='exercise_record_new'),
    path('exercise/record/edit/', views.exercise_record_edit, name='exercise_record_edit'),
    path("exercise/record/delete/<int:pk>/", views.record_delete, name="record_delete"),
    path('favorite', views.FavoriteView.as_view(), name='favorite'),
    path("exercise/favorite/toggle/<int:pk>/", views.toggle_favorite, name="toggle_favorite"),
    path("favorite/add/", views.favorite_add, name="favorite_add"),
    path('mypage/', views.MypageView.as_view(), name='mypage'),
]