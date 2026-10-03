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
    """Secțiunea de Weekend Sprint - complet interactivă"""
    active_plan = WeekendPlan.objects.filter(is_active=True).first()
    all_tasks = Task.objects.filter(is_completed=False)
    subjects = Subject.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. Creare Sprint Nou de Weekend
        if action == 'create_sprint':
            title = request.POST.get('title')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            if active_plan:
                active_plan.is_active = False
                active_plan.save()

            WeekendPlan.objects.create(
                title=title,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            return redirect('weekend_planner')

        # 2. Adăugare Task în Sprint
        elif action == 'add_to_sprint':
            task_id = request.POST.get('task_id')
            if active_plan and task_id:
                task = get_object_or_404(Task, id=task_id)
                active_plan.tasks.add(task)
                return redirect('weekend_planner')

        # 3. Eliminare Task din Sprint
        elif action == 'remove_from_sprint':
            task_id = request.POST.get('task_id')
            if active_plan and task_id:
                task = get_object_or_404(Task, id=task_id)
                active_plan.tasks.remove(task)
                return redirect('weekend_planner')

        # 4. Creare Task Nou Rapid (pe loc)
        elif action == 'quick_create_task':
            subject_id = request.POST.get('subject_id')
            title = request.POST.get('title')
            hours = request.POST.get('estimated_hours', 1.0)
            
            if subject_id and title:
                subject = get_object_or_404(Subject, id=subject_id)
                new_task = Task.objects.create(
                    subject=subject,
                    title=title,
                    estimated_hours=hours
                )
                if active_plan:
                    active_plan.tasks.add(new_task)
                return redirect('weekend_planner')

    context = {
        'plan': active_plan,
        'all_tasks': all_tasks,
        'subjects': subjects,
    }
    return render(request, 'academic/weekend_planner.html', context)

def projects_list(request):
    """Management Proiecte cu salvare rapidă pentru progres și note"""
    if request.method == 'POST':
        action = request.POST.get('action')

        # Adăugare proiect nou
        if action == 'create_project':
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

        # Actualizare status proiect (Ce am făcut / Ce urmează)
        elif action == 'update_project_notes':
            project_id = request.POST.get('project_id')
            project = get_object_or_404(Project, id=project_id)
            project.completed_work = request.POST.get('completed_work', '')
            project.pending_work = request.POST.get('pending_work', '')
            project.next_step = request.POST.get('next_step', '')
            project.save()
            return redirect('projects_list')

        # Adăugare Sub-task rapid direct la un proiect
        elif action == 'add_project_task':
            project_id = request.POST.get('project_id')
            project = get_object_or_404(Project, id=project_id)
            task_title = request.POST.get('task_title')
            if task_title:
                Task.objects.create(
                    subject=project.subject,
                    project=project,
                    title=task_title
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
