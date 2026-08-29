from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # ① 認証まわり
    path('', views.IndexView.as_view(), name='index'),
    path('regist/', views.RegistUserView.as_view(), name='regist'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('logout/', views.UserLogoutView.as_view(), name='user_logout'),

    # ② ホーム
    path('home/', views.home, name='home'),

    # ③ 目標（Goal）
    path('goal/', views.goal_list, name='goal_list'),
    path('goal/create/', views.create_goal, name='create_goal'),
    path('goal/<int:goal_id>/edit/', views.edit_goal, name='edit_goal'),
    path('goal/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('goal/<int:goal_id>/complete/', views.complete_goal, name='complete_goal'),
    path('goal/<int:goal_id>/undo/', views.undo_complete_goal, name='undo_goal'),

    # ④ 予定（ExerciseSchedule）
    path('exercise/new/', views.exercise_new, name='exercise_new'),
    path('exercise/edit/<int:pk>/', views.exercise_edit, name='exercise_edit'),
    path('exercise/delete/<int:pk>/', views.exercise_delete, name='exercise_delete'),

    # ⑤ 記録（ExerciseRecord）
    path('exercise/record/', views.exercise_record, name='exercise_record'),
    path('exercise/record/new/', views.exercise_record_new, name='exercise_record_new'),
    path('exercise/record/<int:pk>/edit/', views.exercise_record_edit, name='exercise_record_edit'),
    path('exercise/record/delete/<int:pk>/', views.record_delete, name='record_delete'),

    # ⑥ お気に入り（Favorite）
    path('favorite/', views.favorite, name='favorite'),
    path('favorite/add/', views.favorite_add, name='favorite_add'),
    path('exercise/favorite/toggle/<int:schedule_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorite/delete/<int:pk>/', views.favorite_delete, name='favorite_delete'),

    # ⑦ マイページ
    path('mypage/', views.MypageView.as_view(), name='mypage'),
]
