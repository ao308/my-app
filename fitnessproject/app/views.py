from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, FormView, View
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from django.contrib.auth.forms import PasswordChangeForm

from .models import Goal, ExerciseSchedule, ExerciseRecord
from .forms import (
    RegistForm, UserLoginForm, GoalForm,
    ExerciseScheduleForm, ExerciseRecordForm,
    EmailChangeForm, CustomPasswordChangeForm,
    FavoriteForm
)

from datetime import datetime, date, time


class IndexView(TemplateView):
    template_name = 'app/index.html'

class HomeView(TemplateView):
    template_name = 'app/home.html'

class RegistUserView(CreateView):
    template_name = 'app/regist.html'
    form_class = RegistForm
    success_url = reverse_lazy('app:user_login')

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

class MypageView(LoginRequiredMixin, TemplateView):
    template_name = 'app/mypage.html'
    login_url = 'app:user_login'

    def get(self, request, *args, **kwargs):
        section = request.GET.get("section")

        email_form = EmailChangeForm()
        password_form = CustomPasswordChangeForm(user=request.user)

        return render(request, self.template_name, {
            "email_form": email_form,
            "password_form": password_form,
            "section": section,
        })

    def post(self, request, *args, **kwargs):
        section = request.GET.get("section")

        if "email_submit" in request.POST:
            email_form = EmailChangeForm(request.POST, instance=request.user)
            password_form = CustomPasswordChangeForm(user=request.user)

            if email_form.is_valid():
                email_form.save()
                messages.success(request, "メールアドレスを変更しました。")
                return redirect("/mypage/?section=email")

        elif "password_submit" in request.POST:
            email_form = EmailChangeForm()
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "パスワードを変更しました。")
                return redirect("/mypage/?section=password")

        return render(request, self.template_name, {
            "email_form": email_form,
            "password_form": password_form,
            "section": section,
        })

@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user).order_by(
        'is_completed',
        'no_deadline',
        'due_date',
        '-id'
    )
    return render(request, 'app/goal.html', {'goals': goals})

@login_required
def edit_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('app:goal_list')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'app/edit_goal.html', {'form': form, 'goal': goal})

@login_required
def home(request):
    goals = Goal.objects.filter(
        user=request.user,
        show_on_home=True,
        is_completed=False
    ).order_by('no_deadline', 'due_date')[:2]

    schedules = ExerciseSchedule.objects.filter(
        user=request.user,
        is_record=False
    ).order_by("date")

    all_schedules = ExerciseSchedule.objects.filter(
        user=request.user,
        is_record=False
    )

    all_records = ExerciseRecord.objects.filter(user=request.user)

    events = [
        {
            "type": "schedule",
            "id": s.pk,
            "title": s.exercise,
            "date": s.date.strftime("%Y-%m-%d") if s.date else "",
            "is_record": s.is_record,
        }
        for s in all_schedules
    ]

    for r in all_records:
        events.append({
            "type": "record",
            "id": r.pk,
            "title": r.exercise,
            "date": r.date.strftime("%Y-%m-%d") if r.date else "",
            "rating": r.rating,
            "is_record": True,
            "schedule": r.schedule_id,
        })

    exercises = schedules.filter(show_on_home=True).order_by("date")[:2]

    return render(request, 'app/home.html', {
        'goals': goals,
        'events': events,
        'exercises': exercises,
        'show_list': True,
    })

@login_required
def create_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('app:goal_list')
    else:
        form = GoalForm()
    return render(request, 'app/create_goal.html', {'form': form})

@login_required
def complete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal.is_completed = True
    goal.save()
    return redirect('app:goal_list')

@login_required
def undo_complete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal.is_completed = False
    goal.save()
    return redirect('app:goal_list') 

@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal.delete()
    return redirect('app:goal_list') 

@login_required
def exercise_new(request):
    date_str = request.GET.get("date")
    exercise_name = request.GET.get("exercise")  # ★ お気に入りから来た運動名

    favorites = ExerciseSchedule.objects.filter(
        user=request.user,
        is_favorite=True
    ).values_list("exercise", flat=True).distinct()

    if request.method == "POST":
        form = ExerciseScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user

            if date_str:
                schedule.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                schedule.date = form.cleaned_data.get("date")

            schedule.save()
            return redirect("app:home")

    else:
        initial = {}

        if date_str:
            try:
                initial["date"] = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        if exercise_name:
            initial["exercise"] = exercise_name  # ★ 自動入力

        form = ExerciseScheduleForm(initial=initial)

    return render(request, "app/exercise_form.html", {
        "form": form,
        "favorites": favorites,  
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ExerciseSchedule, ExerciseRecord
from .forms import ExerciseRecordForm


@login_required
def exercise_record(request):
    schedule_id = request.POST.get("schedule_id") or request.GET.get("id")
    schedule = get_object_or_404(ExerciseSchedule, pk=schedule_id, user=request.user)

    if request.method == "POST":
        form = ExerciseRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.schedule = schedule
            record.exercise = schedule.exercise
            record.date = schedule.date
            record.start_time = schedule.start_time
            record.end_time = schedule.end_time
            record.save()
            schedule.is_record = True
            schedule.show_on_home = False
            schedule.save()

            return redirect("app:home")

        return render(request, "app/exercise_record.html", {
            "form": form,
            "schedule": schedule,
        })

    form = ExerciseRecordForm(initial={
        "exercise": schedule.exercise,
        "date": schedule.date,
        "start_time": schedule.start_time,
        "end_time": schedule.end_time,
    })

    return render(request, "app/exercise_record.html", {
        "form": form,
        "schedule": schedule,
    })

@login_required
def exercise_record_new(request):
    selected_date = request.GET.get("date")

    if request.method == "POST":
        form = ExerciseRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.schedule = None
            record.save()
            return redirect("app:home")

    else:
        if selected_date:
            initial_date = selected_date
        else:
            initial_date = date.today().strftime("%Y-%m-%d")

        form = ExerciseRecordForm(initial={
            "date": initial_date
        })

    favorites = ExerciseSchedule.objects.filter(
        user=request.user,
        is_favorite=True
    ).values_list("exercise", flat=True).distinct()

    return render(request, "app/exercise_record_new.html", {
        "form": form,
        "favorites": favorites,
    })

@login_required
def exercise_edit(request, pk):
    schedule = get_object_or_404(ExerciseSchedule, pk=pk, user=request.user)
    if request.method == "POST":
        form = ExerciseScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect("app:home")
    else:
        form = ExerciseScheduleForm(instance=schedule)

    return render(request, "app/exercise_edit.html", {
        "form": form,
        "schedule": schedule
    })

@login_required
def exercise_delete(request, pk):
    if request.method == "POST":
        try:
            ExerciseSchedule.objects.get(pk=pk, user=request.user).delete()
            return JsonResponse({"success": True})
        except ExerciseSchedule.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"})
    return JsonResponse({"success": False, "error": "Invalid method"})

@login_required
def record_delete(request, pk):
    if request.method == "POST":
        try:
            record = ExerciseRecord.objects.get(pk=pk, user=request.user)
            schedule = record.schedule

            record.delete() 

            schedule.is_record = False
            schedule.show_on_home = True  
            schedule.save()

            return JsonResponse({"success": True})

        except ExerciseRecord.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"})

    return JsonResponse({"success": False, "error": "Invalid method"})

@login_required
def exercise_record_edit(request, pk):
    record = get_object_or_404(ExerciseRecord, pk=pk, user=request.user)

    if request.method == "POST":
        form = ExerciseRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect("app:home")

        return render(request, "app/exercise_record_edit.html", {
            "form": form,
            "record": record,
        })

    form = ExerciseRecordForm(instance=record)

    return render(request, "app/exercise_record_edit.html", {
        "form": form,
        "record": record,
    })

@login_required
def favorite(request):
    favorites = ExerciseSchedule.objects.filter(
        user=request.user,
        is_favorite=True
    ).order_by("-date")

    form = FavoriteForm()

    return render(request, "app/favorite.html", {
        "favorites": favorites,
        "form": form,
    })

@login_required
def toggle_favorite(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    schedule = get_object_or_404(ExerciseSchedule, pk=pk, user=request.user)

    if not schedule.is_favorite:
        ExerciseSchedule.objects.filter(
            user=request.user,
            exercise=schedule.exercise,
            is_favorite=True
        ).exclude(pk=schedule.pk).update(is_favorite=False)

    schedule.is_favorite = not schedule.is_favorite
    schedule.save()

    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        return redirect("app:favorite")

    return JsonResponse({"success": True, "is_favorite": schedule.is_favorite})

@login_required
def favorite_add(request):
    if request.method == "POST":
        form = FavoriteForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["exercise"]

            ExerciseSchedule.objects.filter(
                user=request.user,
                exercise=name,
                is_favorite=True
            ).update(is_favorite=False)

            ExerciseSchedule.objects.create(
                user=request.user,
                exercise=name,
                date=None,
                is_favorite=True,
                is_record=False,
            )

            return redirect("app:favorite")

        favorites = ExerciseSchedule.objects.filter(
            user=request.user,
            is_favorite=True
        ).order_by("-date")

        return render(request, "app/favorite.html", {
            "favorites": favorites,
            "form": form,
            "open_modal": True, 
        })

    return redirect("app:favorite")

