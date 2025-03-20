from django.urls import path
from . import views

app_name = 'core'  # For namespacing

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Project management
    path('projects/', views.project_list, name='project_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:project_id>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:project_id>/save/', views.project_save, name='project_save'),
    path('projects/load/', views.project_load, name='project_load'),
    path('projects/<int:project_id>/tasks/<int:task_id>/update-progress/', views.task_update_progress, name='task_update_progress'),

    
    # Gantt chart and visualization
    path('projects/<int:project_id>/gantt/', views.gantt_chart, name='gantt_chart'),
    path('projects/<int:project_id>/gantt/export/', views.gantt_export, name='gantt_export'),
    path('projects/<int:project_id>/daily/<str:date>/', views.daily_view, name='daily_view'),
    path('projects/<int:project_id>/daily/<str:date>/export/', views.daily_export, name='daily_export'),
    
    # Team management
    path('teams/', views.subteam_list, name='subteam_list'),
    path('teams/new/', views.subteam_create, name='subteam_create'),
    path('teams/<int:subteam_id>/', views.subteam_detail, name='subteam_detail'),
    path('teams/<int:subteam_id>/edit/', views.subteam_edit, name='subteam_edit'),
    path('members/', views.member_list, name='member_list'),

    # Member management
    path('members/new/', views.member_create, name='member_create'),
    path('members/<int:member_id>/', views.member_detail, name='member_detail'),
    path('members/<int:member_id>/edit/', views.member_edit, name='member_edit'),
    
    # Task management
    path('projects/<int:project_id>/tasks/', views.task_list, name='task_list'),
    path('projects/<int:project_id>/tasks/new/', views.task_create, name='task_create'),
    path('projects/<int:project_id>/tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('projects/<int:project_id>/tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    
    # Attendance tracking
    path('projects/<int:project_id>/meetings/', views.meeting_list, name='meeting_list'),
    path('projects/<int:project_id>/meetings/new/', views.meeting_create, name='meeting_create'),
    path('projects/<int:project_id>/meetings/<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),
    path('projects/<int:project_id>/meetings/<int:meeting_id>/attendance/', views.attendance_record, name='attendance_record'),

    # Documentation
    path('documentation/<str:doc_name>/', views.documentation_view, name='documentation'),

    # Accounts
    
]