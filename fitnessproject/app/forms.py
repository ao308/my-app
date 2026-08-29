from django import forms
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from .models import Goal, ExerciseSchedule, ExerciseRecord, Favorite
from datetime import time
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
import re

User = get_user_model()


class RegistForm(forms.ModelForm):
    username = forms.CharField(
        required=False,
        label='ユーザー名',
        widget=forms.TextInput()
    )
    email = forms.EmailField(
        required=False,
        label='メールアドレス',
        widget=forms.EmailInput()
    )
    password = forms.CharField(
        required=False,
        label='パスワード',
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        required=False,
        label='パスワード再入力',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        # 必須チェック（全部ここで）
        if not username:
            self.add_error('username', 'ユーザー名を入力してください')

        if not email:
            self.add_error('email', 'メールアドレスを入力してください')

        if not password:
            self.add_error('password', 'パスワードを入力してください')

        if not password2:
            self.add_error('password2', '入力してください')

        # パスワード一致チェック
        if password and password2 and password != password2:
            self.add_error('password2', 'パスワードが一致しません')

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email and User.objects.filter(email=email).exists():
            self.add_error("email", "このメールアドレスは既に使用されています")

        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if password:
            if not re.search(r"[A-Za-z]", password) or \
               not re.search(r"[0-9]", password) or \
               len(password) < 8:
                self.add_error("password", "パスワードの条件を満たしていません")

        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user

class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="メールアドレス",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="パスワード",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.add_error(None, 'メールアドレスまたはパスワードが正しくありません')
            return cleaned_data

        if not user.check_password(password):
            self.add_error(None, 'メールアドレスまたはパスワードが正しくありません')
            return cleaned_data

        self.user = user
        return cleaned_data

class GoalForm(forms.ModelForm):
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3})
    )

    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = Goal
        fields = ["title", "description", "due_date", "no_deadline", "show_on_home"]
        widgets = {
            "no_deadline": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_on_home": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        due_date = cleaned_data.get("due_date")
        no_deadline = cleaned_data.get("no_deadline")

        if not title:
            self.add_error("title", "目標を入力してください")

        if (due_date and no_deadline) or (not due_date and not no_deadline):
            raise forms.ValidationError(
                "期限は日付を入力するか無期限にチェックを入れてください"
            )

        return cleaned_data


TIME_CHOICES = [
    (time(hour % 24, minute), f"{hour % 24:02d}:{minute:02d}")
    for hour in range(0, 25)
    for minute in (0, 30)
]

class ExerciseScheduleForm(forms.ModelForm):
    memo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2})
    )

    exercise = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={"required": "運動名を入力してください"}
    )

    date = forms.DateField(
        label="日付",
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        error_messages={"required": "日付を選択してください"}
    )

    start_time = forms.TimeField(
        label="開始時間",
        widget=forms.Select(choices=TIME_CHOICES, attrs={"class": "form-select"}),
        error_messages={"required": "開始時間を選択してください"}
    )

    end_time = forms.TimeField(
        label="終了時間",
        widget=forms.Select(choices=TIME_CHOICES, attrs={"class": "form-select"}),
        error_messages={"required": "終了時間を選択してください"}
    )

    show_on_home = forms.BooleanField(
        required=False,
        label="ホーム画面に表示する",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = ExerciseSchedule
        fields = ["exercise", "memo", "date", "start_time", "end_time", "show_on_home"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["exercise"].widget.attrs["id"] = "id_exercise"
        self.fields["memo"].widget.attrs["id"] = "id_memo"

    def clean(self):
        cleaned_data = super().clean()
        exercise = cleaned_data.get("exercise")
        date = cleaned_data.get("date")
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if not exercise:
            self.add_error("exercise", "運動名を入力してください")

        if not date:
            self.add_error("date", "日付を選択してください")

        if start and end and end <= start:
            self.add_error("end_time", "終了時間は開始時間より後にしてください")

        return cleaned_data

class ExerciseRecordForm(forms.ModelForm):
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        input_formats=["%Y-%m-%d"],
        error_messages={"required": "日付を選択してください"}
    )

    exercise = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={"required": "運動名を入力してください"}
    )

    class Meta:
        model = ExerciseRecord
        fields = ["exercise", "memo", "date", "start_time", "end_time", "rating"]
        widgets = {
            "memo": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "start_time": forms.Select(choices=TIME_CHOICES, attrs={"class": "form-select"}),
            "end_time": forms.Select(choices=TIME_CHOICES, attrs={"class": "form-select"}),
            "rating": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "date" in self.initial:
            self.fields["date"].widget.attrs["value"] = self.initial["date"]

    def clean(self):
        cleaned_data = super().clean()
        exercise = cleaned_data.get("exercise")
        date = cleaned_data.get("date")
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")
        rating = cleaned_data.get("rating")

        if not exercise:
            self.add_error("exercise", "運動名を入力してください")

        if not date:
            self.add_error("date", "日付を選択してください")

        if start and end and end <= start:
            self.add_error("end_time", "終了時間は開始時間より後にしてください")

        if rating is None or rating == 0:
            self.add_error("rating", "頑張り度を選択してください")

        return cleaned_data
    
class FavoriteForm(forms.ModelForm):
    exercise = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "運動名を入力",
            }
        ),
        error_messages={"required": "運動名を入力してください"},
    )

    class Meta:
        model = Favorite
        fields = ["exercise"]

class EmailChangeForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        error_messages={"required": "メールアドレスを入力してください"}
    )

    class Meta:
        model = User
        fields = ["email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("メールアドレスを入力してください")

        if self.instance and email == self.instance.email:
            raise forms.ValidationError("現在のメールアドレスと同じです")

        return email

class CustomPasswordChangeForm(BasePasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["old_password"].required = False
        self.fields["new_password1"].required = False
        self.fields["new_password2"].required = False

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs.pop("required", None)

    def clean_old_password(self):
        old = self.cleaned_data.get("old_password")

        if not old:
            raise ValidationError("現在のパスワードを入力してください")

        if not self.user.check_password(old):
            raise ValidationError("現在のパスワードが間違っています")

        return old

    def clean_new_password1(self):
        new_password = self.cleaned_data.get("new_password1")

        if not new_password:
            raise ValidationError("新しいパスワードを入力してください")

        if self.user.check_password(new_password):
            raise ValidationError("現在のパスワードと同じです")

        try:
            validate_password(new_password, self.user)
        except ValidationError:
            raise ValidationError("パスワードの条件を満たしていません")

        return new_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")

        if not new_password2:
            raise ValidationError("入力してください")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError("パスワードが一致しません")

        try:
            validate_password(new_password2, self.user)
        except ValidationError:
            pass

        return new_password2

    def clean(self):
        cleaned_data = super().clean()

        if "new_password2" in self._errors:
            errors = self._errors["new_password2"]

            filtered = [
                e for e in errors
                if "一致しません" in str(e) or "入力してください" in str(e)
            ]

            if filtered:
                self._errors["new_password2"] = filtered
            else:
                del self._errors["new_password2"]

        return cleaned_data





