# Project Persistence: Developer Installation Guide

This guide explains how to implement the Project Persistence feature in the FRC Project Management System.

## Overview

The Project Persistence feature adds the ability to export projects to JSON files and import them back. This implementation includes:

1. Export functionality that serializes all project-related data
2. Import functionality that handles creating entities and maintaining relationships
3. User interface elements for both operations
4. Error handling and progress tracking

## Installation Steps

### 1. Add Template Files

Copy these template files to your project:

- `core/templates/core/project_load.html` - Import form template
- `core/templates/core/import_error.html` - Error handling template

### 2. Update Views

Add these functions to `core/views.py`:

```python
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
        'export_date': datetime.now().isoformat(),
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
                return render(request, 'core/import_error.html', {
                    'error_message': 'Invalid project file format. The file may be corrupted or not a valid project export.',
                    'technical_details': 'Missing format_version or project fields'
                })
            
            rename_duplicates = request.POST.get('rename_duplicates', False) == 'on'
            
            with transaction.atomic():
                # Implementation of project import logic
                # (Full implementation shown in the code examples)
            
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
```

### 3. Update URLs

Ensure your `core/urls.py` includes these paths:

```python
path('projects/<int:project_id>/save/', views.project_save, name='project_save'),
path('projects/load/', views.project_load, name='project_load'),
```

### 4. Add Required Imports

Add these imports to your `views.py`:

```python
import json
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
```

### 5. Update UI Templates

1. Modify `project_list.html` to include the import button:
   ```html
   <div class="d-flex justify-content-between align-items-center mb-4">
       <h1>Projects</h1>
       <div>
           <a href="{% url 'core:project_load' %}" class="btn btn-info me-2">
               <!-- SVG icon here -->
               Import Project
           </a>
           <a href="{% url 'core:project_create' %}" class="btn btn-primary">+ New Project</a>
       </div>
   </div>
   ```

2. Add export buttons to project cards:
   ```html
   <div class="card-footer d-flex justify-content-between">
       <a href="{% url 'core:project_detail' project.id %}" class="btn btn-info">View</a>
       <div>
           <a href="{% url 'core:project_save' project.id %}" class="btn btn-success export-project-btn">
               <!-- SVG icon here -->
               Export
           </a>
           <a href="{% url 'core:project_edit' project.id %}" class="btn btn-warning">Edit</a>
       </div>
   </div>
   ```

3. Add JavaScript to `base.html` for progress tracking (see full implementation in files)

### 6. Testing

Create tests to verify the implementation:

```python
class ProjectPersistenceTests(TestCase):
    def setUp(self):
        # Set up test data (user, project, tasks, etc.)
        pass
        
    def test_project_save(self):
        # Test exporting a project to JSON
        pass
        
    def test_project_load(self):
        # Test importing a project from JSON
        pass
        
    def test_duplicate_project_name_handling(self):
        # Test handling of duplicate project names
        pass
        
    def test_invalid_json_handling(self):
        # Test handling of invalid JSON files
        pass
```

## Common Issues and Solutions

1. **Missing Import Dependencies**
   - Ensure all required modules are imported in `views.py`

2. **Template Resolution**
   - Make sure the templates are in the correct directory structure

3. **JSON Serialization Errors**
   - Use Django's serializers for model objects
   - Use manual mapping for complex relationships

4. **File Upload Configuration**
   - Ensure `enctype="multipart/form-data"` is set on the form
   - Check Django's file upload settings

5. **Database Transactions**
   - Use `with transaction.atomic():` for all import operations
   - This ensures the import is rolled back completely if it fails

6. **Styling Inconsistencies**
   - Ensure SVG icons match the project's style
   - Use consistent button colors and sizes

## Performance Considerations

1. For large projects, consider implementing:
   - Async processing for import/export
   - Background tasks using Celery
   - Progress feedback via WebSockets

2. Export file size optimizations:
   - Remove unnecessary fields
   - Consider pagination or chunking for very large projects

## Security Considerations

1. Always validate imported JSON files
2. Use Django's built-in CSRF protection
3. Ensure proper permissions are checked (login_required)
4. Consider rate limiting for import/export operations