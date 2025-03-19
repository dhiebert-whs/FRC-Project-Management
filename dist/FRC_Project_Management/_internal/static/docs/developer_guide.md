# FRC Project Management System Developer Guide

## System Architecture

The FRC Project Management System is built using Django, a high-level Python web framework. This guide provides information for developers who need to maintain, extend, or customize the application.

### Technology Stack

- **Backend**: Django 5.1.7
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: 
  - Django Templates
  - Bootstrap 5.3
  - JavaScript
  - Chart.js (for data visualization)
- **Additional Libraries**:
  - django-widget-tweaks
  - svgwrite (for Gantt chart export)
  - markdown (for documentation)

## Project Structure

The application follows a standard Django project structure:

```
frc_project_management/         # Main project directory
├── frc_project_management/     # Project settings package
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL routing
│   └── wsgi.py
├── core/                       # Main application package
│   ├── __init__.py
│   ├── admin.py                # Admin interface configuration
│   ├── apps.py
│   ├── forms.py                # Form definitions
│   ├── migrations/             # Database migrations
│   ├── models.py               # Data models
│   ├── templates/              # HTML templates
│   │   └── core/               # Application templates
│   ├── tests.py                # Test cases
│   ├── urls.py                 # App-specific URL routing
│   └── views.py                # View functions
├── static/                     # Static files (CSS, JS, etc.)
│   └── docs/                   # Documentation files
└── manage.py                   # Django command-line utility
```

## Data Models

The system's database schema is defined by the following key models:

### Project Model
Central entity representing a robotics build project.

### Subteam Model
Represents a functional group within the team (e.g., Programming, Mechanical).

### TeamMember Model
Extends the Django User model with additional fields for team management.

### Subsystem Model
Represents a logical component of the robot (e.g., Drivetrain, Arm).

### Task Model
Represents a single work item with dependencies, assignments, and progress tracking.

### Component Model
Represents a physical part or component needed for tasks.

### Meeting Model
Represents a team meeting with date, time, and attendance tracking.

### Attendance Model
Links team members to meetings with presence and timing information.

### Milestone Model
Represents significant project events or deadlines.

## Key Functionality

### Authentication and Authorization

The system uses Django's built-in authentication system. URL patterns in `core/urls.py` are protected with the `@login_required` decorator to ensure only authenticated users can access the application.

### Form Handling

Forms are defined in `core/forms.py` and use Django's ModelForm system with widget customizations from django-widget-tweaks.

### Project Persistence

The Project Persistence functionality allows exporting and importing projects as JSON files, enabling:
- Project backups
- Project sharing between teams
- Version control for projects

#### Export Process

1. The `project_save` view in `core/views.py` serializes a project and all related entities
2. JSON includes project details, tasks, subsystems, members, and relationships
3. File is returned as an attachment with proper content type

#### Import Process

1. The `project_load` view accepts a JSON file upload
2. Validates the file structure and content
3. Uses a database transaction to ensure all-or-nothing import
4. Handles duplicate entity names and relationships
5. Provides error handling for invalid files

## Testing

Tests are defined in `core/tests.py` using Django's testing framework. Run tests with:

```bash
python manage.py test
```

The `ProjectPersistenceTests` class specifically tests the export and import functionality with various scenarios including:
- Successful export and import
- Handling of duplicate project names
- Handling of invalid JSON
- Error cases (empty files, missing data)

## Extending the System

### Adding New Features

To add a new feature:

1. Update the appropriate model(s) in `models.py`
2. Create a migration: `python manage.py makemigrations`
3. Apply the migration: `python manage.py migrate`
4. Add forms in `forms.py`
5. Create view functions in `views.py`
6. Add URL patterns in `urls.py`
7. Create templates in `templates/core/`
8. Add tests in `tests.py`

### Customizing Templates

The system uses Bootstrap 5.3 for styling. To customize the UI:

1. Edit templates in `core/templates/core/`
2. For global changes, modify `base.html`
3. For specific pages, modify the corresponding template

### Adding Export/Import Support for New Entities

If you add new models, update the `project_save` and `project_load` views to include these entities:

1. Add serialization in `project_save`
2. Add deserialization and creation in `project_load`
3. Update tests to verify the new entity is properly exported and imported

## Deployment

### Development Environment

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Production Deployment

For production deployment:

1. Update `settings.py`:
   - Set `DEBUG = False`
   - Update `ALLOWED_HOSTS`
   - Configure a production database (PostgreSQL recommended)
   - Set a secure `SECRET_KEY`

2. Set up a web server (Nginx, Apache) with WSGI (Gunicorn, uWSGI)

3. Configure static file serving:
   ```bash
   python manage.py collectstatic
   ```

4. Set up SSL/TLS for secure connections

## Known Issues and Limitations

1. Task dependencies can create circular references if not careful
2. Large projects with many entities may experience slower export/import times
3. SVG exports have limited styling options

## Future Development Roadmap

1. API endpoints for integration with other systems
2. Enhanced critical path analysis
3. Resource conflict detection
4. Integration with CAD and version control systems
5. Mobile-optimized interface for shop floor use

## Contributing

When contributing to this project:

1. Follow PEP 8 style guidelines for Python code
2. Write tests for new functionality
3. Update documentation to reflect changes
4. Use descriptive commit messages

## Troubleshooting

### Common Development Issues

1. **Migration conflicts**:
   - Create a fresh migration with `--merge` flag:
   ```bash
   python manage.py makemigrations --merge
   ```

2. **Template rendering errors**:
   - Check context variables passed to the template
   - Verify template inheritance hierarchy

3. **Form validation issues**:
   - Inspect form errors in view by printing `form.errors`
   - Check model constraints and form validation rules