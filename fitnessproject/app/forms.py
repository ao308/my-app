from django import forms
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password

User = get_user_model()

class RegistForm(forms.ModelForm):
    password2 = forms.CharField(
        label='パスワード再入力',
        widget=forms.PasswordInput()
    )

    class Meta():
        model = User
        fields = ['username', 'email', 'password']
        widgets ={
            'password': forms.PasswordInput(),
        }
        labels ={
            'username': 'ユーザー名',
            'email': 'メールアドレス',
            'password': 'パスワード',
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if email and User.objects.filter(email=email).exists():
            self.add_error('email','このメールアドレスは既に登録されています')
        if password and len(password) < 8:
            self.add_error('password','パスワードは8文字以上で入力してください')
        if password and password2 and password != password2:
            self.add_error('password2','パスワードが一致しません')
        return cleaned_data
    
    def save(self, commit=True):
        user = super(). save(commit=False)
        validate_password(self.cleaned_data['password'], user)
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

    


    