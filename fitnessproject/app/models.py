from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not email:
            raise ValueError('Emailを入力してください')
        if not password:
            raise ValueError('Passwordを入力してください')
        user = self.model(
            username=username,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, email, password):
        user = self.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def get_absolute_url(self):
        return reverse_lazy('app:home')

    class Meta:
        db_table = 'user'
        managed = True

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField("目標", max_length=100)
    description = models.TextField("詳細", blank=True)
    due_date = models.DateField("期限", null=True, blank=True)
    no_deadline = models.BooleanField("無期限", default=False)
    show_on_home = models.BooleanField("ホームに表示", default=False)
    is_completed = models.BooleanField(default=False) 
    
    def __str__(self):
        return self.title

class ExerciseSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.CharField(max_length=100)
    memo = models.TextField(blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    show_on_home = models.BooleanField(default=False)
    is_record = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.exercise} ({self.date} {self.start_time}-{self.end_time})"
    
class ExerciseRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(ExerciseSchedule, on_delete=models.CASCADE)
    memo = models.TextField(blank=True)
    rating = models.IntegerField(null=False, blank=False)  # ★必須
    time = models.IntegerField(null=True, blank=True)    # 任意
    
    created_at = models.DateTimeField(auto_now_add=True)