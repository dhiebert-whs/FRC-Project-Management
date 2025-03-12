from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm
from django.http import HttpResponse
from .models import Subteam, Task, Meeting, Attendance, TeamMember
from django.utils import timezone

# Dashboard
@login_required
def dashboard(request):
    projects = Project.objects.all()
    return render(request, 'core/dashboard.html', {'projects': projects})

# Project views
@login_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'core/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Project "{project.name}" was created successfully!')
            return redirect('core:project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    return render(request, 'core/project_form.html', {'form': form, 'title': 'Create New Project'})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'core/project_detail.html', {'project': project})

@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" was updated successfully!')
            return redirect('core:project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'core/project_form.html', {'form': form, 'project': project, 'title': 'Edit Project'})

@login_required
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" was deleted successfully!')
        return redirect('core:project_list')
    
    return render(request, 'core/project_confirm_delete.html', {'project': project})

# Project file management views (these were mentioned before but not implemented)
@login_required
def project_save(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # TODO: Implement project saving to file
    messages.info(request, f'Project "{project.name}" export functionality coming soon.')
    return redirect('core:project_detail', project_id=project.id)

@login_required
def project_load(request):
    if request.method == 'POST':
        # TODO: Implement project loading from file
        messages.info(request, 'Project import functionality coming soon.')
        return redirect('core:project_list')
    return render(request, 'core/project_load.html')

# Gantt chart and visualization views
@login_required
def gantt_chart(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'core/gantt_chart.html', {'project': project})

@login_required
def gantt_export(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # TODO: Implement SVG export
    messages.info(request, 'Gantt chart export functionality coming soon.')
    return redirect('core:gantt_chart', project_id=project.id)

@login_required
def daily_view(request, project_id, date):
    project = get_object_or_404(Project, id=project_id)
    # TODO: Parse date and show daily view
    return render(request, 'core/daily_view.html', {'project': project, 'date': date})

@login_required
def daily_export(request, project_id, date):
    project = get_object_or_404(Project, id=project_id)
    # TODO: Implement daily view SVG export
    messages.info(request, 'Daily view export functionality coming soon.')
    return redirect('core:daily_view', project_id=project.id, date=date)

# Team management views
@login_required
def subteam_list(request):
    subteams = Subteam.objects.all()
    return render(request, 'core/subteam_list.html', {'subteams': subteams})

@login_required
def subteam_create(request):
    if request.method == 'POST':
        form = SubteamForm(request.POST)
        if form.is_valid():
            subteam = form.save()
            messages.success(request, f'Subteam "{subteam.name}" was created successfully!')
            return redirect('core:subteam_detail', subteam_id=subteam.id)
    else:
        form = SubteamForm()
    
    return render(request, 'core/subteam_form.html', {'form': form, 'title': 'Create New Subteam'})


@login_required
def subteam_detail(request, subteam_id):
    subteam = get_object_or_404(Subteam, id=subteam_id)
    return render(request, 'core/subteam_detail.html', {'subteam': subteam})

@login_required
def subteam_edit(request, subteam_id):
    subteam = get_object_or_404(Subteam, id=subteam_id)
    
    if request.method == 'POST':
        form = SubteamForm(request.POST, instance=subteam)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subteam "{subteam.name}" was updated successfully!')
            return redirect('core:subteam_detail', subteam_id=subteam.id)
    else:
        form = SubteamForm(instance=subteam)
    
    return render(request, 'core/subteam_form.html', {'form': form, 'subteam': subteam, 'title': 'Edit Subteam'})

# Task management views
@login_required
def task_list(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Get all tasks for the project
    tasks = Task.objects.filter(project=project)
    
    # Apply filters
    status = request.GET.get('status')
    if status == 'completed':
        tasks = tasks.filter(completed=True)
    elif status == 'incomplete':
        tasks = tasks.filter(completed=False)
    
    subsystem_id = request.GET.get('subsystem')
    if subsystem_id:
        tasks = tasks.filter(subsystem_id=subsystem_id)
    
    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)
    
    member_id = request.GET.get('member')
    if member_id:
        tasks = tasks.filter(assigned_to__id=member_id)
    
    # Get filter choices
    subsystems = Subsystem.objects.all()
    team_members = TeamMember.objects.all()
    priority_choices = Task.PRIORITY_CHOICES
    
    context = {
        'project': project,
        'tasks': tasks,
        'subsystems': subsystems,
        'team_members': team_members,
        'priority_choices': priority_choices,
    }
    
    return render(request, 'core/task_list.html', context)


@login_required
def task_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            
            # Save many-to-many relationships
            form.save_m2m()
            
            messages.success(request, f'Task "{task.title}" was created successfully!')
            return redirect('core:task_detail', project_id=project.id, task_id=task.id)
    else:
        form = TaskForm(project=project)
    
    return render(request, 'core/task_form.html', {
        'form': form, 
        'project': project, 
        'title': 'Create New Task'
    })

@login_required
def task_detail(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id, project=project)
    
    return render(request, 'core/task_detail.html', {
        'project': project,
        'task': task,
    })


@login_required
def task_edit(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id, project=project)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" was updated successfully!')
            return redirect('core:task_detail', project_id=project.id, task_id=task.id)
    else:
        form = TaskForm(instance=task, project=project)
    
    return render(request, 'core/task_form.html', {
        'form': form, 
        'project': project, 
        'task': task,
        'title': 'Edit Task'
    })

@login_required
def task_update_progress(request, project_id, task_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        task = get_object_or_404(Task, id=task_id, project=project)
        
        progress = int(request.POST.get('progress', task.progress))
        
        # Update progress and set completed if 100%
        task.progress = min(100, max(0, progress))  # Ensure 0-100 range
        if task.progress == 100:
            task.completed = True
        task.save()
        
        messages.success(request, f'Task progress updated to {task.progress}%')
        
    return redirect('core:task_detail', project_id=project_id, task_id=task_id)

# Attendance tracking views
@login_required
def meeting_list(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    meetings = Meeting.objects.filter(project=project)
    return render(request, 'core/meeting_list.html', {'project': project, 'meetings': meetings})

@login_required
def meeting_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # TODO: Implement meeting creation form
    messages.info(request, 'Meeting creation functionality coming soon.')
    return redirect('core:meeting_list', project_id=project.id)

@login_required
def meeting_detail(request, project_id, meeting_id):
    project = get_object_or_404(Project, id=project_id)
    meeting = get_object_or_404(Meeting, id=meeting_id, project=project)
    return render(request, 'core/meeting_detail.html', {'project': project, 'meeting': meeting})

@login_required
def attendance_record(request, project_id, meeting_id):
    project = get_object_or_404(Project, id=project_id)
    meeting = get_object_or_404(Meeting, id=meeting_id, project=project)
    # TODO: Implement attendance recording form
    messages.info(request, 'Attendance recording functionality coming soon.')
    return redirect('core:meeting_detail', project_id=project.id, meeting_id=meeting.id)


