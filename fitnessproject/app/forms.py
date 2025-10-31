from django import forms
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

User = get_user_model()

class RegistForm(forms.ModelForm):

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

    def save(self, commit=False):
        user = super(). save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

class UserLoginForm(forms.Form):
    email = forms.EmailField(label="メールアドレス")
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError('メールアドレスまたはパスワードが正しくありません')
            self.user = user
        return cleaned_data

    