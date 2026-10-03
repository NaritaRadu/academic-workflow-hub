from django.shortcuts import render,redirect, get_object_or_404
from django.utils import timezone
from .models import Subject, Project, Task,TestPrep,DebugLog,WeekendPlan


# Create your views here.


def dashboard(request):
    #Pagina principala: Statistici rapide, Proiecte Active, Task uri urgente
    subjects=Subject.objects.all()
    active_projects=Project.objects.all().order_by('deadline')
    urgent_tasks=Task.objects.filter(is_completed=False).order_by('due_date','-priority')[:8]
    
    current_weekend=WeekendPlan.objects.filter(is_active=True).first()
    
    context={
        'subjects':subjects,
        'active_projects':active_projects,
        'urgent_tasks':urgent_tasks,
        'current_weekend':current_weekend,
        'now':timezone.now(),
    }
    return render(request,'academic/dashboard.html',context)

def toggle_task(request,task_id):
    #Actiune rapida pentru a bifa/debifa un task
    task=get_object_or_404(Task,id=task_id)
    task.is_completed=not task.is_completed
    task.save()
    
    referer=request.META.get('HTTP_REFERER')
    return redirect(referer if referer else 'dashboard')

def weekend_planner(request):
    #Sectiunea dedicata sprintului de weekend
    active_plan=WeekendPlan.objects.filter(is_active=True).first()
    all_tasks=Task.objects.filter(is_completed=False)
    
    if request.method=='POST' and 'add_task_id' in request.POST:
        task_id=request.POST.get('add_task_id')
        if active_plan and task_id:
            task=get_object_or_404(Task,id=task_id)
            active_plan.tasks.add(task)
            return redirect('weekend_planner')
    
    context={
        'plan':active_plan,
        'all_tasks':all_tasks,
    }
    return render(request,'academic/weekend_planner.html',context)

def projects_list(request):
    #Tracker detaliat de proiecte
    projects=Project.objects.all().order_by('deadline')
    return render(request,'academic/projects.html',{'projects':projects})

def debug_log_list(request):
    logs=DebugLog.objects.all().order_by('-created_at')
    return render(request,'academic/debug_logs.html',{'logs':logs})
