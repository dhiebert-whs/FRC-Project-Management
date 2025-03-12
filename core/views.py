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
    # TODO: Implement subteam creation form
    messages.info(request, 'Subteam creation functionality coming soon.')
    return redirect('core:dashboard')

@login_required
def subteam_detail(request, subteam_id):
    subteam = get_object_or_404(Subteam, id=subteam_id)
    return render(request, 'core/subteam_detail.html', {'subteam': subteam})

@login_required
def subteam_edit(request, subteam_id):
    subteam = get_object_or_404(Subteam, id=subteam_id)
    # TODO: Implement subteam edit form
    messages.info(request, 'Subteam editing functionality coming soon.')
    return redirect('core:subteam_detail', subteam_id=subteam.id)

# Task management views
@login_required
def task_list(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)
    return render(request, 'core/task_list.html', {'project': project, 'tasks': tasks})

@login_required
def task_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # TODO: Implement task creation form
    messages.info(request, 'Task creation functionality coming soon.')
    return redirect('core:project_detail', project_id=project.id)

@login_required
def task_detail(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id, project=project)
    return render(request, 'core/task_detail.html', {'project': project, 'task': task})

@login_required
def task_edit(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id, project=project)
    # TODO: Implement task edit form
    messages.info(request, 'Task editing functionality coming soon.')
    return redirect('core:task_detail', project_id=project.id, task_id=task.id)

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