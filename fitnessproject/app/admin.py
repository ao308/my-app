from django.contrib import admin
from .models import Goal, ExerciseSchedule, ExerciseRecord
from django.contrib import admin
from .models import User

admin.site.register(User)

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'show_on_home')
    exclude = ('user',)
    list_filter = ('show_on_home',)
    search_fields = ('title', 'user__username')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(ExerciseSchedule)
class ExerciseScheduleAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'user', 'date', 'is_record')
    list_filter = ('is_record', 'date')
    search_fields = ('exercise', 'user__username')


@admin.register(ExerciseRecord)
class ExerciseRecordAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'user', 'date', 'rating')
    list_filter = ('date', 'rating')
    search_fields = ('exercise', 'user__username')