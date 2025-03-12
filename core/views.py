from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm

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
