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
from django.shortcuts import render, get_object_or_404, redirect
from .models import Goal
from .forms import GoalForm


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
    
class ObjectiveView(LoginRequiredMixin, TemplateView):
    template_name = 'app/objective.html'
    login_url = 'app:user_login'

class FavoriteView(LoginRequiredMixin, TemplateView):
    template_name = 'app/favorite.html'
    login_url = 'app:user_login'

class MypageView(LoginRequiredMixin, TemplateView):
    template_name = 'app/mypage.html'
    login_url = 'app:user_login'


def objective_list(request):
    goals = Goal.objects.filter(user=request.user)
    return render(request, 'app/objective.html', {'goals': goals})

def edit_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('app:objective')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'app/edit_goal.html', {'form': form, 'goal': goal})


def home(request):
    goals = Goal.objects.filter(user=request.user, show_on_home=True)
    return render(request, 'app/home.html', {'goals': goals})

@login_required
def create_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('app:objective')
    else:
        form = GoalForm()
    return render(request, 'app/create_goal.html', {'form': form})

@login_required
def complete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal.is_completed = True
    goal.save()
    return redirect('app:objective') 

@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal.delete()
    return redirect('app:home') 
