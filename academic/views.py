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

def subject_detail(request, subject_id):
    """Pagina dedicată unei singure materii (ex: Click pe SO2)"""
    subject = get_object_or_404(Subject, id=subject_id)
    projects = subject.projects.all()
    tasks = subject.tasks.filter(is_completed=False)
    debug_logs = subject.debug_logs.all().order_by('-created_at')

    context = {
        'subject': subject,
        'projects': projects,
        'tasks': tasks,
        'debug_logs': debug_logs,
    }
    return render(request, 'academic/subject_detail.html', context)

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
    """Listă proiecte + formular adăugare rapidă"""
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        repo_url = request.POST.get('repository_url')
        deadline = request.POST.get('deadline')

        if subject_id and title and deadline:
            subject = get_object_or_404(Subject, id=subject_id)
            Project.objects.create(
                subject=subject,
                title=title,
                description=description,
                repository_url=repo_url,
                deadline=deadline
            )
            return redirect('projects_list')

    projects = Project.objects.all().order_by('deadline')
    subjects = Subject.objects.all()
    return render(request, 'academic/projects.html', {'projects': projects, 'subjects': subjects})

def debug_log_list(request):
    """Jurnal debugging + formular adăugare eroare nouă"""
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        title = request.POST.get('title')
        error_message = request.POST.get('error_message')
        solution = request.POST.get('solution')

        if subject_id and title and solution:
            subject = get_object_or_404(Subject, id=subject_id)
            DebugLog.objects.create(
                subject=subject,
                title=title,
                error_message=error_message,
                solution=solution
            )
            return redirect('debug_log_list')

    logs = DebugLog.objects.all().order_by('-created_at')
    subjects = Subject.objects.all()
    return render(request, 'academic/debug_logs.html', {'logs': logs, 'subjects': subjects})
