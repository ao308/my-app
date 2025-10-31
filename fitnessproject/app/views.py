from django.shortcuts import render, redirect
from django.views.generic import (
    TemplateView, CreateView, FormView, View
)
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .forms import RegistForm, UserLoginForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

class IndexView(TemplateView):
    template_name = 'app/index.html'

class HomeView(TemplateView):
    template_name = 'app/home.html'

class RegistUserView(CreateView):
    template_name = 'app/regist.html'
    form_class = RegistForm
    success_url = reverse_lazy('app:home')

class UserLoginView(FormView):
    template_name = 'app/user_login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('app:home')

    def form_valid(self, form):   
        login(self.request, form.user)
        return super(). form_valid(form)
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        print('next: ', next_url)
        return next_url if next_url else self.success_url

class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('app:user_login')
    
class UserView(LoginRequiredMixin, TemplateView):
    template_name = 'user.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


    
