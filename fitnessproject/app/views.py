from django.shortcuts import render, redirect
from . import forms
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'app/index.html')
    
def regist(request):
    regist_form = forms.RegistForm(request.POST or None)
    if regist_form.is_valid():
        regist_form.save(commit=True)
        return redirect('app:home')
    return render(
        request, 'app/regist.html', context={
            'regist_form': regist_form,
        }
    ) 
    
def user_login(request):
    login_form = forms.LoginForm(request.POST or None)
    if login_form.is_valid():
        email = login_form.cleaned_data['email']
        password = login_form.cleaned_data['password']
        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
            return redirect('app:home')
        else:
            messages.warning(request, 'ログインに失敗しました')
    return render(
        request, 'app/user_login.html', context={
            'login_form': login_form,
        }
    )
@login_required
def user_logout(request):
    logout(request)
    return redirect('app:home.html')
