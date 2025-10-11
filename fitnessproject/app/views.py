from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'app/index.html')
    
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # ログイン後の遷移先
        else:
            messages.error(request, 'ユーザー名またはパスワードが正しくありません。')

    return render(request, 'app/login.html')

@login_required
def home_view(request):
    return render(request, 'home.html')
