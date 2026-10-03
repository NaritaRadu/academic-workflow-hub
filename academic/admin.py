from django.contrib import admin
from .models import Subject, Project, Task, TestPrep, DebugLog , WeekendPlan

# Register your models here.

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display=('name','code','professor','color_code')
    search_fields=('name','code','professor')
    
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display=('title','subject','deadline','get_progress','created_at')
    list_filter=('subject','deadline')
    search_fields=('title','description','next_step')
    
    @admin.display(description="Progress (%)")
    def get_progress(self,obj):
        return f"{obj.progress_percentage}%"
    
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'priority', 'due_date', 'estimated_hours', 'is_completed')
    list_filter = ('is_completed', 'subject', 'priority', 'due_date')
    search_fields = ('title', 'notes')
    list_editable = ('is_completed', 'priority')


@admin.register(TestPrep)
class TestPrepAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'test_date')
    list_filter = ('subject', 'test_date')
    search_fields = ('title', 'topics_to_cover', 'solved_questions')


@admin.register(DebugLog)
class DebugLogAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('title', 'error_message', 'solution')


@admin.register(WeekendPlan)
class WeekendPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'get_progress')
    list_filter = ('is_active',)
    filter_horizontal = ('tasks',)

    @admin.display(description='Progres Sprint (%)')
    def get_progress(self, obj):
        return f"{obj.progress_percentage}% ({obj.completed_tasks_count}/{obj.total_tasks})"