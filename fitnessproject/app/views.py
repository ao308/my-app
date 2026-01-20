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
from .models import Goal, ExerciseSchedule, ExerciseRecord
from .forms import GoalForm, ExerciseScheduleForm, ExerciseRecordForm
from datetime import time, datetime
from django.http import JsonResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import EmailChangeForm, CustomPasswordChangeForm

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

    def get(self, request, *args, **kwargs):
        favorites = ExerciseSchedule.objects.filter(
            user=request.user,
            is_favorite=True
        ).order_by("-date")

        return render(request, self.template_name, {
            "favorites": favorites
        })

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

        # メールアドレス変更
        if "email_submit" in request.POST:
            email_form = EmailChangeForm(request.POST, instance=request.user)
            password_form = CustomPasswordChangeForm(user=request.user)

            if email_form.is_valid():
                email_form.save()
                return redirect("app:mypage")

        # パスワード変更
        elif "password_submit" in request.POST:
            email_form = EmailChangeForm()
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect("app:mypage")

        return render(request, self.template_name, {
            "email_form": email_form,
            "password_form": password_form,
            "section": section,
        })


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

@login_required
def home(request):
    goals = Goal.objects.filter(user=request.user, show_on_home=True)

    # ホーム画面に出すのは未記録だけ
    schedules = ExerciseSchedule.objects.filter(
        user=request.user,
        is_record=False
    ).order_by("date")

# カレンダー用は全件（記録済みも含む）
    all_schedules = ExerciseSchedule.objects.filter(user=request.user)
    all_records = ExerciseRecord.objects.filter(user=request.user)

# 予定（ExerciseSchedule）
    events = [
        {
            "type": "schedule",
            "id": s.pk,
            "title": s.exercise,
            "date": s.date.strftime("%Y-%m-%d"),
            "is_record": s.is_record,
        }
        for s in all_schedules
    ]

# 記録（ExerciseRecord）
    events += [
        {
            "type": "record",
            "id": r.pk,
            "title": r.schedule.exercise,
            "date": r.schedule.date.strftime("%Y-%m-%d"),
            "rating": r.rating,
        }
        for r in all_records
    ]

    # ★ここだけ修正！
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

@login_required
def exercise_new(request):
    date_str = request.GET.get("date")
    exercise_name = request.GET.get("exercise")  # ★ お気に入りから来た運動名

    # ★ お気に入り一覧を取得
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
        "favorites": favorites,  # ★ テンプレートへ渡す
    })

@login_required
def exercise_record(request):
    pk = request.GET.get("id")
    schedule = get_object_or_404(ExerciseSchedule, pk=pk, user=request.user)

    if request.method == "POST":
        form = ExerciseRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.schedule = schedule
            record.save()

            schedule.is_record = True
            schedule.show_on_home = False
            schedule.save()

            return redirect("app:home")
        else:
            # ★ バリデーションエラー時は form をそのまま返す
            return render(request, "app/exercise_record.html", {
                "form": form,
                "schedule": schedule,
            })

    else:
        form = ExerciseRecordForm()

    return render(request, "app/exercise_record.html", {
        "form": form,
        "schedule": schedule,
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
            schedule = record.schedule  # 対応する予定を取得

            record.delete()  # 記録を削除

            # ★ 予定を「未記録」に戻す
            schedule.is_record = False
            schedule.show_on_home = True  # 必要ならホームに戻す
            schedule.save()

            return JsonResponse({"success": True})

        except ExerciseRecord.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"})

    return JsonResponse({"success": False, "error": "Invalid method"})

@login_required
def exercise_record_edit(request):
    pk = request.GET.get("id")
    record = get_object_or_404(ExerciseRecord, pk=pk, user=request.user)
    schedule = record.schedule

    if request.method == "POST":
        form = ExerciseRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect("app:home")
    else:
        form = ExerciseRecordForm(instance=record)

    return render(request, "app/exercise_record.html", {
        "form": form,
        "schedule": schedule,
    })

@login_required
def toggle_favorite(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    schedule = get_object_or_404(ExerciseSchedule, pk=pk, user=request.user)
    schedule.is_favorite = not schedule.is_favorite
    schedule.save()

    # ★ ページからのフォーム送信ならリダイレクト
    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        return redirect("app:favorite")

    return JsonResponse({"success": True, "is_favorite": schedule.is_favorite})