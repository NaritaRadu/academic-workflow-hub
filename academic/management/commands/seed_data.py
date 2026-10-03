from django.core.management.base import BaseCommand
from academic.models import Subject

class Command(BaseCommand):
    help="Populeaza baza de date cu materiile de anul 3 TI"
    
    def handle(self,*args,**kwargs):
        subject_data=[
            {'name':'Sisteme de Operare 2 (SO2)',
            'code':'SO2',
            'color_code':'#EF4444',
            },
            {'name':'Proiectarea cu Microprocesoare (PM)',
            'code':'PM',
            'color_code':'#F59E0B',
            },
            {'name':'Bazele Inteligenței Artificiale (BIA)',
            'code':'BIA',
            'color_code':'#10B981',
            },
            {'name':'Administrarea Bazelor de Date (ABD)',
            'code':'ABD',
            'color_code':'#3B82F6',
            },
            {'name':'Modelare și Simulare (MS)',
             'code':'MS',
             'color_code':'#8B5CF6',
            },
            {
            'name': 'Ingineria Traficului și Sisteme de Calcul (ITSC / FIC)',
            'code': 'ITSC',
            'color_code': '#EC4899',  
            },
        ]
        
        created_count=0
        for data in subject_data:
            subject,created=Subject.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name':data['name'],
                    'color_code':data['color_code'],
                }
            )
            if created:
                created_count+=1
                self.stdout.write(self.style.SUCCESS(f"A fost creata materia:{subject.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Materia {subject.code} exista deja."))
        self.stdout.write(self.style.SUCCESS(f"\nProces finalizat! {created_count} materii adaugate"))        