from django.db import models
from django.utils import timezone
# Create your models here.

class Subject(models.Model):
    #Materiile din semestru
    name=models.CharField(max_length=100)
    code=models.CharField(max_length=20,blank=True)
    professor=models.CharField(max_length=100,blank=True)
    color_code=models.CharField(max_length=7,default="#3B82F6",help_text="culoare hex pentru UI")
    
    def __str__(self):
        return self.name
    
class Project(models.Model):
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="projects")
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    repository_url = models.URLField(blank=True, help_text="Link GitHub/GitLab/Drive")
    deadline=models.DateTimeField()
    next_step=models.TextField(blank=True,help_text="Urmatorul pas concret de facut la proiect")
    created_at=models.DateTimeField(auto_now_add=True)
    
    @property
    def progress_percentage(self):
        #Calculeaza automat procentul de finalizare bazat pe sub-taskuri
        total=self.tasks.count()
        if total==0:
            return 0
        completed=self.tasks.filter(is_completed=True).count()
        return int((completed/total)*100)
    
    def __str__(self):
        return f"[{self.subject.name}] {self.title}"

class Task(models.Model):
    PRIORITY_CHOICES=[
        ('LOW', 'Scăzută'),
        ('MEDIUM', 'Medie'),
        ('HIGH', 'Ridicată'),
    ]
    
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="tasks")
    project=models.ForeignKey(Project,on_delete=models.CASCADE,null=True,blank=True,related_name="tasks")
    title=models.CharField(max_length=200)
    notes=models.TextField(blank=True,help_text="ce mai trebuie adaugat / detalii")
    priority=models.CharField(max_length=10,choices=PRIORITY_CHOICES,default="MEDIUM")
    estimated_hours=models.FloatField(default=1.0)
    is_completed=models.BooleanField(default=False)
    due_date=models.DateTimeField(null=True,blank=True)
    completed_at=models.DateTimeField(null=True,blank=True)
    
    def save(self,*args,**kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at=timezone.now()
        elif not self.is_completed:
            self.completed_at=None
        super().save(*args,**kwargs)
        
    def __str__(self):
        return f"[{self.subject.name}] {self.title}"

class TestPrep(models.Model):
    #Material de pregatire si intrebari/rezolvari pentru teste,examene
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="test_preps")
    title=models.CharField(max_length=200,help_text="ex: Test Laborator 1")
    test_date=models.DateTimeField()
    topics_to_cover=models.TextField(help_text="Lista de concepte / capitole de invatat")
    solved_questions=models.TextField(blank=True,help_text="Intrebari frecvente si rezolvari")
    
    def __str__(self):
        return f"Prep Test:{self.subject.name}-{self.title}"
    
class DebugLog(models.Model):
    #Jurnal de debugging pentru laboratoare
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="debug_logs")
    title=models.CharField(max_length=200,help_text="ex:Segfault in alocatorul de memorie")
    error_message=models.TextField(blank=True)
    solution=models.TextField(help_text="Cum am rezolvat eroarea / explicatia")
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Debug [{self.subject.name}]:{self.title}"
    

class WeekendPlan(models.Model):
    title=models.CharField(max_length=100,help_text="ex: Plan weekend 4-5 Octombrie")
    start_date=models.DateField()
    end_date=models.DateField()
    tasks=models.ManyToManyField(Task,blank=True,related_name="weekend_plans")
    is_active=models.BooleanField(default=True)
    
    @property
    def total_tasks(self):
        return self.tasks.count()
    
    @property
    def completed_tasks_count(self):
        return self.tasks.filter(is_completed=True).count()
    
    @property
    def remaining_tasks_count(self):
        return self.total_tasks-self.completed_tasks_count
    
    @property
    def progress_percentage(self):
        total=self.total_tasks
        if total==0:
            return 0
        return int((self.completed_tasks_count/total)*100)
    
    def __str__(self):
        return self.title
            
    
    
    
        