from django.db import models
from django.utils import timezone
# Create your models here.

class Subject(models.Model):
    #Materiile din semestru
    name=models.CharField(max_length=100)
    code=models.CharField(max_length=20,blank=True)
    professor=models.CharField(max_length=100,blank=True)
    color_code=models.CharField(max_length=7,default="#3B82F6",help_text="culoare hex pentru UI")
    FORMULA_CHOICES = [
        ('50_50', 'Medie Aritmetică (50% Activitate / 50% Examen)'),
        ('33_66', '33% Activitate / 66% Examen'),
        ('40_60', '40% Activitate / 60% Examen'),
        ('30_70', '30% Activitate / 70% Examen'),
    ]
    grading_formula = models.CharField(
        max_length=10, 
        choices=FORMULA_CHOICES, 
        default='50_50',
        help_text="Modul de combinare între Nota de Activitate și Nota de Examen"
    )
    
    def __str__(self):
        return self.name
    
    @property
    def activity_grade(self):
        """Calculează Nota de Activitate (media aritmetică a testelor și proiectelor de la laborator)"""
        act_components = self.grade_components.filter(category='ACTIVITY', obtained_grade__isnull=False)
        if not act_components.exists():
            return None
        
        total = sum(c.obtained_grade for c in act_components)
        return round(total / act_components.count(), 2)

    @property
    def exam_grade(self):
        """Preluăm nota obținută la Examen (dacă s-a susținut)"""
        exam_comp = self.grade_components.filter(category='EXAM', obtained_grade__isnull=False).first()
        return exam_comp.obtained_grade if exam_comp else None

    @property
    def final_grade(self):
        """Calculează Nota Finală bazat pe Nota de Activitate, Nota de Examen și Formula selectată"""
        act = self.activity_grade
        ex = self.exam_grade

        if act is None and ex is None:
            return 0.0

        # Determinăm ponderile
        if self.grading_formula == '50_50':
            w_act, w_ex = 0.50, 0.50
        elif self.grading_formula == '33_66':
            w_act, w_ex = 0.3333, 0.6667
        elif self.grading_formula == '40_60':
            w_act, w_ex = 0.40, 0.60
        elif self.grading_formula == '30_70':
            w_act, w_ex = 0.30, 0.70
        else:
            w_act, w_ex = 0.50, 0.50

        # Dacă s-a susținut doar activitatea
        if ex is None:
            return round(act * w_act, 2)
        # Dacă s-a susținut doar examenul
        if act is None:
            return round(ex * w_ex, 2)

        # Calcul complet
        return round((act * w_act) + (ex * w_ex), 2)

    def needed_exam_grade(self, target_final_grade=5.0):
        """Calculează cât îți trebuie la EXAMEN pentru a atinge o notă țintă (ex: 5 sau 8)"""
        act = self.activity_grade
        if act is None:
            act = 0.0 # Presupunem 0 dacă nu are încă activitate

        if self.grading_formula == '50_50':
            w_act, w_ex = 0.50, 0.50
        elif self.grading_formula == '33_66':
            w_act, w_ex = 0.3333, 0.6667
        elif self.grading_formula == '40_60':
            w_act, w_ex = 0.40, 0.60
        elif self.grading_formula == '30_70':
            w_act, w_ex = 0.30, 0.70
        else:
            w_act, w_ex = 0.50, 0.50

        # Formula: Final = (Act * w_act) + (Examen * w_ex)
        # Examen = (Final - (Act * w_act)) / w_ex
        needed = (target_final_grade - (act * w_act)) / w_ex
        
        if needed <= 1.0:
            return 1.0 # Ai trecut deja din punctajul de activitate!
        return round(needed, 2)
        
class Project(models.Model):
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="projects")
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    repository_url = models.URLField(blank=True, help_text="Link GitHub/GitLab/Drive")
    deadline=models.DateTimeField()
    completed_work = models.TextField(blank=True, help_text="Ce am realizat până acum")
    pending_work = models.TextField(blank=True, help_text="Ce mai trebuie adăugat / de făcut")
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


class GradeComponent(models.Model):
    CATEGORY_CHOICES = [
        ('ACTIVITY', 'Activitate / Laborator / Proiect'),
        ('EXAM', 'Examen Final'),
    ]
    
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="grade_components")
    name=models.CharField(max_length=100,help_text="ex:Examen Final, Proiect PM, Test Lab 1")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='ACTIVITY')
    obtained_grade=models.FloatField(null=True,blank=True,help_text="Nota obtinuta")
    
    
    def __str__(self):
        grade_str=f"{self.obtained_grade}" if self.obtained_grade else "Nesustinut"
        return f"[{self.subject.code}] {self.name} ({self.weight_percentage}%) - Nota:{grade_str}" 
       
    
    
        