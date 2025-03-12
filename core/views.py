from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms import modelformset_factory
from .models import Project, Subteam, Task, Meeting, Attendance, TeamMember, Component, Milestone, Subsystem
from .forms import ProjectForm, SubteamForm, TaskForm, MeetingForm, AttendanceForm, TeamMemberForm
from django.http import HttpResponse, JsonResponse
from .models import Subteam, Task, Meeting, Attendance, TeamMember
from django.shortcuts import render, redirect, get_object_or_404
from django.core import serializers
from django.db import transaction
from django.utils import timezone
from django.utils.timedelta import duration_string
from datetime import timedelta

import svgwrite
import markdown
import json
import os
import datetime


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
    """
    Export a project and all its related data to a JSON file
    """
    project = get_object_or_404(Project, id=project_id)
    
    # Get related data
    tasks = Task.objects.filter(project=project)
    subsystems = set()
    for task in tasks:
        subsystems.add(task.subsystem)
    
    milestones = project.milestones.all()
    meetings = project.meetings.all()
    
    # Collect all components and team members referenced by tasks
    components = set()
    team_members = set()
    for task in tasks:
        components.update(task.required_components.all())
        team_members.update(task.assigned_to.all())
    
    # Get subteams for all team members
    subteams = set()
    for member in team_members:
        if member.subteam:
            subteams.add(member.subteam)
    
    # Serialize all data using Django's serializers
    project_data = {
        'project': json.loads(serializers.serialize('json', [project]))[0],
        'tasks': json.loads(serializers.serialize('json', tasks)),
        'subsystems': json.loads(serializers.serialize('json', subsystems)),
        'milestones': json.loads(serializers.serialize('json', milestones)),
        'meetings': json.loads(serializers.serialize('json', meetings)),
        'components': json.loads(serializers.serialize('json', components)),
        'team_members': json.loads(serializers.serialize('json', team_members)),
        'subteams': json.loads(serializers.serialize('json', subteams)),
        'export_date': datetime.datetime.now().isoformat(),
        'format_version': '1.0'
    }
    
    # Handle many-to-many relationships for tasks
    task_relations = {}
    for task in tasks:
        task_relations[task.id] = {
            'pre_dependencies': [dep.id for dep in task.pre_dependencies.all()],
            'required_components': [comp.id for comp in task.required_components.all()],
            'assigned_to': [member.id for member in task.assigned_to.all()]
        }
    project_data['task_relations'] = task_relations
    
    # For attendance records
    attendance_data = []
    for meeting in meetings:
        attendances = meeting.attendances.all()
        attendance_data.extend(json.loads(serializers.serialize('json', attendances)))
    project_data['attendance'] = attendance_data
    
    # Create response
    response = HttpResponse(
        json.dumps(project_data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="{project.name.replace(" ", "_")}.json"'
    return response

@login_required
def project_load(request):
    """
    Import a project from a JSON file
    """
    if request.method == 'POST' and request.FILES.get('project_file'):
        try:
            project_file = request.FILES['project_file']
            project_data = json.loads(project_file.read().decode('utf-8'))
            
            # Validate the format
            if 'format_version' not in project_data or 'project' not in project_data:
                messages.error(request, 'Invalid project file format. The file may be corrupted or not a valid project export.')
                return redirect('core:project_list')
            
            rename_duplicates = request.POST.get('rename_duplicates', False) == 'on'
            
            with transaction.atomic():
                # Import project
                project_import = project_data['project']
                project_fields = project_import['fields']
                
                # Check for duplicate project name
                project_name = project_fields['name']
                if Project.objects.filter(name=project_name).exists() and rename_duplicates:
                    original_name = project_name
                    counter = 1
                    while Project.objects.filter(name=project_name).exists():
                        project_name = f"{original_name} (Import {counter})"
                        counter += 1
                    project_fields['name'] = project_name
                
                # Create new project
                new_project = Project.objects.create(
                    name=project_fields['name'],
                    description=project_fields.get('description', ''),
                    start_date=project_fields['start_date'],
                    goal_end_date=project_fields['goal_end_date'],
                    hard_deadline=project_fields['hard_deadline']
                )
                
                # Mapping dictionaries to keep track of old IDs to new IDs
                subteam_map = {}
                subsystem_map = {}
                component_map = {}
                member_map = {}
                task_map = {}
                
                # Import subteams first
                for subteam_import in project_data.get('subteams', []):
                    subteam_fields = subteam_import['fields']
                    # Check if subteam already exists by name
                    existing_subteam = Subteam.objects.filter(name=subteam_fields['name']).first()
                    if existing_subteam:
                        subteam_map[subteam_import['pk']] = existing_subteam.id
                    else:
                        new_subteam = Subteam.objects.create(
                            name=subteam_fields['name'],
                            color_code=subteam_fields['color_code'],
                            specialties=subteam_fields.get('specialties', '')
                        )
                        subteam_map[subteam_import['pk']] = new_subteam.id
                
                # Import components
                for component_import in project_data.get('components', []):
                    component_fields = component_import['fields']
                    # Check if component already exists by name and part number
                    existing_component = Component.objects.filter(
                        name=component_fields['name'],
                        part_number=component_fields.get('part_number', '')
                    ).first()
                    if existing_component:
                        component_map[component_import['pk']] = existing_component.id
                    else:
                        new_component = Component.objects.create(
                            name=component_fields['name'],
                            part_number=component_fields.get('part_number', ''),
                            description=component_fields.get('description', ''),
                            expected_delivery=component_fields.get('expected_delivery'),
                            actual_delivery=component_fields.get('actual_delivery'),
                            is_delivered=component_fields.get('is_delivered', False)
                        )
                        component_map[component_import['pk']] = new_component.id
                
                # Import subsystems
                for subsystem_import in project_data.get('subsystems', []):
                    subsystem_fields = subsystem_import['fields']
                    
                    # Map subteam if exists
                    responsible_subteam_id = None
                    if subsystem_fields.get('responsible_subteam'):
                        responsible_subteam_id = subteam_map.get(subsystem_fields['responsible_subteam'])
                    
                    # Check if subsystem already exists by name
                    existing_subsystem = Subsystem.objects.filter(name=subsystem_fields['name']).first()
                    if existing_subsystem:
                        subsystem_map[subsystem_import['pk']] = existing_subsystem.id
                    else:
                        new_subsystem = Subsystem.objects.create(
                            name=subsystem_fields['name'],
                            description=subsystem_fields.get('description', ''),
                            status=subsystem_fields.get('status', 'not_started'),
                            responsible_subteam_id=responsible_subteam_id
                        )
                        subsystem_map[subsystem_import['pk']] = new_subsystem.id
                
                # Import team members (Note: requires existing User objects)
                # In practice, we would match on username or create new users
                for member_import in project_data.get('team_members', []):
                    member_fields = member_import['fields']
                    
                    # Try to find the existing user
                    user = None
                    try:
                        user = User.objects.get(id=member_fields['user'])
                    except ObjectDoesNotExist:
                        # Skip this member if the user doesn't exist
                        continue
                    
                    # Map subteam if exists
                    subteam_id = None
                    if member_fields.get('subteam'):
                        subteam_id = subteam_map.get(member_fields['subteam'])
                    
                    # Check if member already exists
                    existing_member = TeamMember.objects.filter(user=user).first()
                    if existing_member:
                        member_map[member_import['pk']] = existing_member.id
                    else:
                        new_member = TeamMember.objects.create(
                            user=user,
                            subteam_id=subteam_id,
                            phone=member_fields.get('phone', ''),
                            skills=member_fields.get('skills', ''),
                            is_leader=member_fields.get('is_leader', False)
                        )
                        member_map[member_import['pk']] = new_member.id
                
                # Import milestones
                for milestone_import in project_data.get('milestones', []):
                    milestone_fields = milestone_import['fields']
                    Milestone.objects.create(
                        project=new_project,
                        name=milestone_fields['name'],
                        description=milestone_fields.get('description', ''),
                        date=milestone_fields['date']
                    )
                
                # Import tasks
                for task_import in project_data.get('tasks', []):
                    task_fields = task_import['fields']
                    
                    # Map subsystem
                    subsystem_id = subsystem_map.get(task_fields['subsystem'])
                    if not subsystem_id:
                        # Skip task if subsystem is missing
                        continue
                    
                    # Create task
                    new_task = Task.objects.create(
                        project=new_project,
                        title=task_fields['title'],
                        description=task_fields.get('description', ''),
                        estimated_duration=task_fields['estimated_duration'],
                        actual_duration=task_fields.get('actual_duration'),
                        priority=task_fields.get('priority', 2),
                        progress=task_fields.get('progress', 0),
                        start_date=task_fields.get('start_date'),
                        end_date=task_fields.get('end_date'),
                        completed=task_fields.get('completed', False),
                        subsystem_id=subsystem_id
                    )
                    task_map[task_import['pk']] = new_task.id
                
                # Add task relations
                task_relations = project_data.get('task_relations', {})
                for old_task_id, relations in task_relations.items():
                    if old_task_id not in task_map:
                        continue
                    
                    task = Task.objects.get(id=task_map[int(old_task_id)])
                    
                    # Add pre_dependencies
                    for dep_id in relations.get('pre_dependencies', []):
                        if dep_id in task_map:
                            task.pre_dependencies.add(Task.objects.get(id=task_map[dep_id]))
                    
                    # Add required_components
                    for comp_id in relations.get('required_components', []):
                        if comp_id in component_map:
                            task.required_components.add(Component.objects.get(id=component_map[comp_id]))
                    
                    # Add assigned team members
                    for member_id in relations.get('assigned_to', []):
                        if member_id in member_map:
                            task.assigned_to.add(TeamMember.objects.get(id=member_map[member_id]))
                
                # Import meetings and attendance records can be implemented similarly
                # but are omitted here for brevity
            
            messages.success(request, f'Project "{new_project.name}" imported successfully!')
            return redirect('core:project_detail', project_id=new_project.id)
            
        except json.JSONDecodeError as e:
            return render(request, 'core/import_error.html', {
                'error_message': 'Invalid JSON format. The file may be corrupted.',
                'technical_details': str(e)
            })
        except Exception as e:
            return render(request, 'core/import_error.html', {
                'error_message': f'Error importing project: {str(e)}',
                'technical_details': str(e)
            })
    
    return render(request, 'core/project_load.html')

# Gantt chart and visualization views
@login_required
def gantt_chart(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project).select_related('subsystem')
    
    # Calculate overall project progress
    if tasks.exists():
        completed_tasks = tasks.filter(completed=True).count()
        overall_progress = int((completed_tasks / tasks.count()) * 100)
    else:
        overall_progress = 0
    
    # Count tasks by priority
    priority_counts = {}
    for priority_id, _ in Task.PRIORITY_CHOICES:
        priority_counts[priority_id] = tasks.filter(priority=priority_id).count()
    
    # Get milestone information
    milestones = project.milestones.all()
    total_milestones = milestones.count()
    completed_milestones = milestones.filter(date__lte=timezone.now().date()).count()
    
    # Prepare task data for JavaScript
    tasks_json = []
    for task in tasks:
        # Get subsystem and subteam information
        subsystem_name = task.subsystem.name if task.subsystem else "Unassigned"
        subteam_name = task.subsystem.responsible_subteam.name if task.subsystem and task.subsystem.responsible_subteam else "Unassigned"
        
        # Get assigned members
        assigned_members = [member.user.get_full_name() or member.user.username for member in task.assigned_to.all()]
        
        # Calculate estimated duration in days
        est_duration_days = task.estimated_duration.days
        if task.estimated_duration.seconds > 0:
            est_duration_days += 1
        
        task_data = {
            'id': task.id,
            'title': task.title,
            'progress': task.progress,
            'priority': task.priority,
            'project_id': project.id,
            'subsystem_name': subsystem_name,
            'subteam_name': subteam_name,
            'assigned_members': assigned_members,
            'start_date': task.start_date.isoformat() if task.start_date else project.start_date.isoformat(),
            'end_date': task.end_date.isoformat() if task.end_date else None,
            'estimated_duration_days': est_duration_days,
            'completed': task.completed,
        }
        tasks_json.append(task_data)
    
    context = {
        'project': project,
        'tasks_json': json.dumps(tasks_json),
        'overall_progress': overall_progress,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': tasks.count() - completed_tasks,
        'priority_counts': priority_counts,
        'total_milestones': total_milestones,
        'completed_milestones': completed_milestones,
    }
    
    return render(request, 'core/gantt_chart.html', context)


@login_required
def gantt_export(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project).select_related('subsystem')
    
    # Create SVG
    dwg = svgwrite.Drawing('gantt_chart.svg', profile='tiny', size=('1200px', '800px'))
    
    # Add title
    dwg.add(dwg.text(f'Gantt Chart - {project.name}', insert=(50, 30), style='font-size:20px; font-weight:bold;'))
    
    # Calculate date range
    start_date = project.start_date
    end_date = project.hard_deadline
    days_range = (end_date - start_date).days + 1
    
    # Draw grid
    grid_start_y = 80
    grid_end_y = 600
    day_width = min(30, (1100 / days_range))
    
    # Draw vertical lines for dates
    for i in range(days_range + 1):
        x = 100 + (i * day_width)
        dwg.add(dwg.line((x, grid_start_y - 20), (x, grid_end_y), stroke='#cccccc', stroke_width=1))
        
        # Add date labels for every 5 days
        if i % 5 == 0:
            date_label = (start_date + timedelta(days=i)).strftime('%m/%d')
            dwg.add(dwg.text(date_label, insert=(x - 15, grid_start_y - 5), style='font-size:10px;'))
    
    # Draw horizontal lines and task bars
    y_pos = grid_start_y
    for i, task in enumerate(tasks):
        # Task name
        dwg.add(dwg.text(task.title[:30], insert=(10, y_pos + 15), style='font-size:12px;'))
        
        # Calculate task position
        task_start = task.start_date if task.start_date else start_date
        task_end = task.end_date if task.end_date else (task_start + task.estimated_duration)
        
        task_start_x = 100 + ((task_start - start_date).days * day_width)
        task_duration_days = (task_end - task_start).days + 1
        task_width = max(2, task_duration_days * day_width)
        
        # Task bar color based on completion
        bar_color = '#4caf50' if task.completed else '#2196f3'
        
        # Draw task bar
        dwg.add(dwg.rect((task_start_x, y_pos + 5), (task_width, 20), 
                         fill=bar_color, stroke='#000000', stroke_width=1))
        
        # Draw progress bar
        if task.progress > 0 and not task.completed:
            progress_width = (task.progress / 100) * task_width
            dwg.add(dwg.rect((task_start_x, y_pos + 5), (progress_width, 20), 
                             fill='#8bc34a', stroke='none'))
        
        # Horizontal line below task
        dwg.add(dwg.line((100, y_pos + 30), (100 + (days_range * day_width), y_pos + 30), 
                         stroke='#eeeeee', stroke_width=1))
        
        y_pos += 40
    
    # Return SVG as response
    svg_content = dwg.tostring()
    response = HttpResponse(svg_content, content_type='image/svg+xml')
    response['Content-Disposition'] = f'attachment; filename="gantt_chart_{project.name}.svg"'
    return response

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
    meetings = Meeting.objects.filter(project=project).order_by('-date', '-start_time')
    
    today = timezone.now().date()
    upcoming_meetings = meetings.filter(date__gte=today)
    past_meetings = meetings.filter(date__lt=today)
    
    context = {
        'project': project,
        'upcoming_meetings': upcoming_meetings,
        'past_meetings': past_meetings,
    }
    
    return render(request, 'core/meeting_list.html', context)

@login_required
@login_required
def meeting_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.project = project
            meeting.save()
            
            messages.success(request, 'Meeting created successfully. Now you can record attendance.')
            return redirect('core:attendance_record', project_id=project.id, meeting_id=meeting.id)
    else:
        # Default to today's date
        form = MeetingForm(initial={'date': timezone.now().date()})
    
    return render(request, 'core/meeting_form.html', {
        'form': form,
        'project': project,
        'title': 'Schedule New Meeting'
    })

@login_required
def meeting_detail(request, project_id, meeting_id):
    project = get_object_or_404(Project, id=project_id)
    meeting = get_object_or_404(Meeting, id=meeting_id, project=project)
    attendances = meeting.attendances.all().select_related('member', 'member__user', 'member__subteam')
    
    # Count statistics
    total_members = TeamMember.objects.count()
    present_members = attendances.filter(present=True).count()
    absent_members = total_members - present_members
    attendance_percentage = (present_members / total_members * 100) if total_members > 0 else 0
    
    context = {
        'project': project,
        'meeting': meeting,
        'attendances': attendances,
        'total_members': total_members,
        'present_members': present_members,
        'absent_members': absent_members,
        'attendance_percentage': attendance_percentage,
    }
    
    return render(request, 'core/meeting_detail.html', context)

@login_required
def attendance_record(request, project_id, meeting_id):
    project = get_object_or_404(Project, id=project_id)
    meeting = get_object_or_404(Meeting, id=meeting_id, project=project)
    
    # Get all team members
    members = TeamMember.objects.all().select_related('user', 'subteam')
    
    # Create or get attendance records for each member
    if request.method == 'POST':
        for member in members:
            member_id = str(member.id)
            if f'present_{member_id}' in request.POST:
                present = request.POST.get(f'present_{member_id}') == 'on'
                arrival_time = request.POST.get(f'arrival_{member_id}') or None
                departure_time = request.POST.get(f'departure_{member_id}') or None
                
                attendance, created = Attendance.objects.get_or_create(
                    meeting=meeting,
                    member=member,
                    defaults={
                        'present': present,
                        'arrival_time': arrival_time,
                        'departure_time': departure_time
                    }
                )
                
                if not created:
                    attendance.present = present
                    attendance.arrival_time = arrival_time
                    attendance.departure_time = departure_time
                    attendance.save()
        
        messages.success(request, 'Attendance recorded successfully.')
        return redirect('core:meeting_detail', project_id=project.id, meeting_id=meeting.id)
    
    # Prepare data for the form
    attendance_data = {}
    for attendance in Attendance.objects.filter(meeting=meeting):
        attendance_data[attendance.member.id] = {
            'present': attendance.present,
            'arrival_time': attendance.arrival_time,
            'departure_time': attendance.departure_time
        }
    
    context = {
        'project': project,
        'meeting': meeting,
        'members': members,
        'attendance_data': attendance_data,
    }
    
    return render(request, 'core/attendance_form.html', context)

#members
@login_required
def member_list(request):
    members = TeamMember.objects.all().select_related('user', 'subteam')
    return render(request, 'core/member_list.html', {'members': members})

@login_required
def member_create(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'Team member "{member}" was created successfully!')
            return redirect('core:member_detail', member_id=member.id)
    else:
        form = TeamMemberForm()
    
    return render(request, 'core/member_form.html', {'form': form, 'title': 'Add Team Member'})

@login_required
def member_detail(request, member_id):
    member = get_object_or_404(TeamMember, id=member_id)
    return render(request, 'core/member_detail.html', {'member': member})

@login_required
def member_edit(request, member_id):
    member = get_object_or_404(TeamMember, id=member_id)
    
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f'Team member "{member}" was updated successfully!')
            return redirect('core:member_detail', member_id=member.id)
    else:
        form = TeamMemberForm(instance=member)
    
    return render(request, 'core/member_form.html', {'form': form, 'member': member, 'title': 'Edit Team Member'})


# Documentation view
@login_required
def documentation_view(request, doc_name):
    """
    View to render documentation files from Markdown to HTML
    """
    # Define the path to your documentation file
    doc_path = os.path.join(settings.BASE_DIR, 'static', 'docs', f'{doc_name}.md')
    
    # Default content if file not found
    content = "Documentation not found."
    title = "Documentation"
    
    # Try to read the markdown file
    if os.path.exists(doc_path):
        with open(doc_path, 'r') as f:
            md_content = f.read()
            # Convert Markdown to HTML
            content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
            
            # Extract title from first h1 heading
            lines = md_content.split('\n')
            if lines and lines[0].startswith('# '):
                title = lines[0][2:]
    else:
        # If the file doesn't exist but we're in development mode,
        # generate placeholder documentation
        if settings.DEBUG:
            if doc_name == 'user_guide':
                content = markdown.markdown("""
# FRC Project Management System User Guide

This is placeholder content for the user guide. The actual documentation file 
should be placed at `static/docs/user_guide.md`.

## Key Features

- Project management
- Task tracking
- Team organization
- Gantt chart visualization
- Meeting attendance

## Project Export/Import

The system allows you to export projects to files and import them back, which is
useful for:

- Creating backups of your projects
- Sharing project templates with other teams
- Version control for complex projects

To export a project, navigate to the project detail page and click "Save to File".
To import a project, go to the projects list and click "Import Project".
                """)
                title = "User Guide"
            elif doc_name == 'developer_guide':
                content = markdown.markdown("""
# FRC Project Management System Developer Guide

This is placeholder content for the developer guide. The actual documentation file 
should be placed at `static/docs/developer_guide.md`.

## Technical Overview

- Django-based web application
- Bootstrap for UI
- Project export/import functionality
- Testing with Django's test framework

## Project Persistence

The project persistence feature allows exporting projects to JSON files and importing
them back. The implementation is in `views.py` in the `project_save` and `project_load`
functions. The export creates a JSON representation of a project and all its related
entities, while the import recreates the project from the JSON file.

Tests for this functionality are in the `ProjectPersistenceTests` class in `tests.py`.
                """)
                title = "Developer Guide"
    
    return render(request, 'core/documentation.html', {
        'content': content,
        'title': title,
        'doc_name': doc_name
    })
            
    try:
        project_file = request.FILES['project_file']
        
        # Check if file is empty
        if project_file.size == 0:
            return render(request, 'core/import_error.html', {
                'error_message': 'The uploaded file is empty.',
                'technical_details': 'File has zero bytes.'
            })
            
        # Read and parse JSON
        try:
            project_data = json.loads(project_file.read().decode('utf-8'))
        except json.JSONDecodeError as e:
            return render(request, 'core/import_error.html', {
                'error_message': 'Invalid JSON format. The file may be corrupted or not a proper JSON file.',
                'technical_details': str(e)
            })
        
        # Validate the format
        if 'format_version' not in project_data or 'project' not in project_data:
            return render(request, 'core/import_error.html', {
                'error_message': 'Invalid project file format. The file may be corrupted or not a valid project export.',
                'technical_details': 'Missing required format_version or project data.'
            })
        
        rename_duplicates = request.POST.get('rename_duplicates', False) == 'on'
        
        with transaction.atomic():
            # Import project
            project_import = project_data['project']
            project_fields = project_import['fields']
            
            # Check for duplicate project name
            project_name = project_fields['name']
            if Project.objects.filter(name=project_name).exists():
                if not rename_duplicates:
                    return render(request, 'core/import_error.html', {
                        'error_message': f'A project with the name "{project_name}" already exists.',
                        'technical_details': 'Set the "rename duplicates" option to automatically rename the imported project.'
                    })
                
                original_name = project_name
                counter = 1
                while Project.objects.filter(name=project_name).exists():
                    project_name = f"{original_name} (Import {counter})"
                    counter += 1
                project_fields['name'] = project_name
            
            # Create new project
            new_project = Project.objects.create(
                name=project_fields['name'],
                description=project_fields.get('description', ''),
                start_date=project_fields['start_date'],
                goal_end_date=project_fields['goal_end_date'],
                hard_deadline=project_fields['hard_deadline']
            )
            
            # Mapping dictionaries to keep track of old IDs to new IDs
            subteam_map = {}
            subsystem_map = {}
            component_map = {}
            member_map = {}
            task_map = {}
            
            # Import subteams first
            for subteam_import in project_data.get('subteams', []):
                subteam_fields = subteam_import['fields']
                # Check if subteam already exists by name
                existing_subteam = Subteam.objects.filter(name=subteam_fields['name']).first()
                if existing_subteam:
                    subteam_map[subteam_import['pk']] = existing_subteam.id
                else:
                    new_subteam = Subteam.objects.create(
                        name=subteam_fields['name'],
                        color_code=subteam_fields['color_code'],
                        specialties=subteam_fields.get('specialties', '')
                    )
                    subteam_map[subteam_import['pk']] = new_subteam.id
            
            # Import components
            for component_import in project_data.get('components', []):
                component_fields = component_import['fields']
                # Check if component already exists by name and part number
                existing_component = Component.objects.filter(
                    name=component_fields['name'],
                    part_number=component_fields.get('part_number', '')
                ).first()
                if existing_component:
                    component_map[component_import['pk']] = existing_component.id
                else:
                    new_component = Component.objects.create(
                        name=component_fields['name'],
                        part_number=component_fields.get('part_number', ''),
                        description=component_fields.get('description', ''),
                        expected_delivery=component_fields.get('expected_delivery'),
                        actual_delivery=component_fields.get('actual_delivery'),
                        is_delivered=component_fields.get('is_delivered', False)
                    )
                    component_map[component_import['pk']] = new_component.id
            
            # Import subsystems
            for subsystem_import in project_data.get('subsystems', []):
                subsystem_fields = subsystem_import['fields']
                
                # Map subteam if exists
                responsible_subteam_id = None
                if subsystem_fields.get('responsible_subteam'):
                    responsible_subteam_id = subteam_map.get(subsystem_fields['responsible_subteam'])
                
                # Check if subsystem already exists by name
                existing_subsystem = Subsystem.objects.filter(name=subsystem_fields['name']).first()
                if existing_subsystem:
                    subsystem_map[subsystem_import['pk']] = existing_subsystem.id
                else:
                    new_subsystem = Subsystem.objects.create(
                        name=subsystem_fields['name'],
                        description=subsystem_fields.get('description', ''),
                        status=subsystem_fields.get('status', 'not_started'),
                        responsible_subteam_id=responsible_subteam_id
                    )
                    subsystem_map[subsystem_import['pk']] = new_subsystem.id
            
            # Import team members (Note: requires existing User objects)
            # In practice, we would match on username or create new users
            for member_import in project_data.get('team_members', []):
                member_fields = member_import['fields']
                
                # Try to find the existing user
                user = None
                try:
                    user = User.objects.get(id=member_fields['user'])
                except ObjectDoesNotExist:
                    # Skip this member if the user doesn't exist
                    continue
                
                # Map subteam if exists
                subteam_id = None
                if member_fields.get('subteam'):
                    subteam_id = subteam_map.get(member_fields['subteam'])
                
                # Check if member already exists
                existing_member = TeamMember.objects.filter(user=user).first()
                if existing_member:
                    member_map[member_import['pk']] = existing_member.id
                else:
                    new_member = TeamMember.objects.create(
                        user=user,
                        subteam_id=subteam_id,
                        phone=member_fields.get('phone', ''),
                        skills=member_fields.get('skills', ''),
                        is_leader=member_fields.get('is_leader', False)
                    )
                    member_map[member_import['pk']] = new_member.id
            
            # Import milestones
            for milestone_import in project_data.get('milestones', []):
                milestone_fields = milestone_import['fields']
                Milestone.objects.create(
                    project=new_project,
                    name=milestone_fields['name'],
                    description=milestone_fields.get('description', ''),
                    date=milestone_fields['date']
                )
            
            # Import meetings
            meeting_map = {}
            for meeting_import in project_data.get('meetings', []):
                meeting_fields = meeting_import['fields']
                new_meeting = Meeting.objects.create(
                    project=new_project,
                    date=meeting_fields['date'],
                    start_time=meeting_fields['start_time'],
                    end_time=meeting_fields['end_time'],
                    notes=meeting_fields.get('notes', '')
                )
                meeting_map[meeting_import['pk']] = new_meeting.id
            
            # Import tasks
            for task_import in project_data.get('tasks', []):
                task_fields = task_import['fields']
                
                # Map subsystem
                subsystem_id = subsystem_map.get(task_fields['subsystem'])
                if not subsystem_id:
                    # Skip task if subsystem is missing
                    continue
                
                # Create task
                new_task = Task.objects.create(
                    project=new_project,
                    title=task_fields['title'],
                    description=task_fields.get('description', ''),
                    estimated_duration=task_fields['estimated_duration'],
                    actual_duration=task_fields.get('actual_duration'),
                    priority=task_fields.get('priority', 2),
                    progress=task_fields.get('progress', 0),
                    start_date=task_fields.get('start_date'),
                    end_date=task_fields.get('end_date'),
                    completed=task_fields.get('completed', False),
                    subsystem_id=subsystem_id
                )
                task_map[task_import['pk']] = new_task.id
            
            # Add task relations
            task_relations = project_data.get('task_relations', {})
            for old_task_id, relations in task_relations.items():
                if old_task_id not in task_map:
                    continue
                
                task = Task.objects.get(id=task_map[int(old_task_id)])
                
                # Add pre_dependencies
                for dep_id in relations.get('pre_dependencies', []):
                    if dep_id in task_map:
                        task.pre_dependencies.add(Task.objects.get(id=task_map[dep_id]))
                
                # Add required_components
                for comp_id in relations.get('required_components', []):
                    if comp_id in component_map:
                        task.required_components.add(Component.objects.get(id=component_map[comp_id]))
                
                # Add assigned team members
                for member_id in relations.get('assigned_to', []):
                    if member_id in member_map:
                        task.assigned_to.add(TeamMember.objects.get(id=member_map[member_id]))
            
            # Import attendance records
            for attendance_import in project_data.get('attendance', []):
                attendance_fields = attendance_import['fields']
                
                # Map meeting and member
                meeting_id = meeting_map.get(attendance_fields['meeting'])
                member_id = member_map.get(attendance_fields['member'])
                
                if not meeting_id or not member_id:
                    continue
                
                Attendance.objects.create(
                    meeting_id=meeting_id,
                    member_id=member_id,
                    present=attendance_fields.get('present', False),
                    arrival_time=attendance_fields.get('arrival_time'),
                    departure_time=attendance_fields.get('departure_time')
                )
        
        messages.success(request, f'Project "{new_project.name}" imported successfully!')
        return redirect('core:project_detail', project_id=new_project.id)
        
    except Exception as e:
        return render(request, 'core/import_error.html', {
            'error_message': f'Error importing project: {str(e)}',
            'technical_details': str(e)
        })
    
    return render(request, 'core/project_load.html')