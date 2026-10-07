from django.urls import path
from . import views

urlpatterns=[
    path('',views.dashboard,name='dashboard'),
    path('grades/', views.grade_calculator, name='grade_calculator'),
    path('flashcards/', views.flashcards_view, name='flashcards_view'),
    path('subject/manage/', views.manage_subjects, name='manage_subjects'),
    path('study-tracker/', views.study_tracker, name='study_tracker'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('task/<int:task_id>/toggle/',views.toggle_task,name='toggle_task'),
    path('task/add/', views.add_task, name='add_task'),
    path('weekend/',views.weekend_planner,name='weekend_planner'),
    path('projects/',views.projects_list,name='projects_list'),
    path('debug-logs/',views.debug_log_list,name='debug_log_list'),
]