from django import forms
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from .models import Goal, ExerciseSchedule, ExerciseRecord
from datetime import time
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
import re

User = get_user_model()

class RegistForm(forms.ModelForm):
    password2 = forms.CharField(
        label='パスワード再入力',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }
        labels = {
            'username': 'ユーザー名',
            'email': 'メールアドレス',
            'password': 'パスワード',
        }

    def clean_password(self):
        password = self.cleaned_data.get("password")

        # 半角英字チェック
        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("パスワードには半角英字を含めてください。")

        # 半角数字チェック
        if not re.search(r"[0-9]", password):
            raise ValidationError("パスワードには半角数字を含めてください。")

        # 8文字以上チェック（Django標準でもチェックされるが明示）
        if len(password) < 8:
            raise ValidationError("パスワードは8文字以上で入力してください。")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            self.add_error('password2', 'パスワードが一致しません')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user



class UserLoginForm(forms.Form):
    email = forms.EmailField(label="メールアドレス")
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError('メールアドレスまたはパスワードが正しくありません')

        if not user.check_password(password):
            raise ValidationError('メールアドレスまたはパスワードが正しくありません')

        self.user = user
        return cleaned_data
    
class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        exclude = ['user']
        fields = ['title', 'description', 'due_date', 'no_deadline', 'show_on_home']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get("due_date")
        no_deadline = cleaned_data.get("no_deadline")

        if (due_date and no_deadline) or (not due_date and not no_deadline):
            self.add_error("due_date", "期限を入力するか、無期限にチェックを入れてください（両方は不可）")

        return cleaned_data

TIME_CHOICES = [
    (time(hour % 24, minute), f"{hour % 24:02d}:{minute:02d}")
    for hour in range(0, 25)   # 0〜24時まで
    for minute in (0, 30)      # 0分と30分
]

class ExerciseScheduleForm(forms.ModelForm):
    date = forms.DateField(
        label="日付",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    start_time = forms.TimeField(
        label="開始時間",
        widget=forms.Select(choices=TIME_CHOICES, attrs={"class": "form-select"})
    )
    end_time = forms.TimeField(
        label="終了時間",
        widget=forms.Select(choices=TIME_CHOICES, attrs={"class": "form-select"})
    )

    class Meta:
        model = ExerciseSchedule
        fields = ["exercise", "memo", "date", "start_time", "end_time", "show_on_home"]
        widgets = {
            "show_on_home": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "show_on_home": "ホーム画面に表示する",
        }
        
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if start and end and end <= start:
            self.add_error("end_time", "終了時間は開始時間より後にしてください")

        return cleaned_data
    
class ExerciseRecordForm(forms.ModelForm):
    class Meta:
        model = ExerciseRecord
        fields = ["memo", "rating"]
        widgets = {
            "memo": forms.Textarea(attrs={"class": "form-control"}),
            "rating": forms.HiddenInput(),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if rating in [None, 0]:
            raise forms.ValidationError("頑張り度を選択してください")
        return rating

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 表示時は空欄にする
        self.fields["email"].initial = ""


class CustomPasswordChangeForm(BasePasswordChangeForm):
    """Bootstrap対応のパスワード変更フォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
