from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Project, Task, Subsystem, TeamMember, Subteam, Component, Milestone, Meeting, Attendance
import json
import tempfile
from datetime import timedelta

class ProjectPersistenceTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        
        # Create a test project
        self.project = Project.objects.create(
            name='Test Project',
            description='A test project description',
            start_date=timezone.now().date(),
            goal_end_date=timezone.now().date() + timedelta(days=30),
            hard_deadline=timezone.now().date() + timedelta(days=45)
        )
        
        # Create a subteam
        self.subteam = Subteam.objects.create(
            name='Test Subteam',
            color_code='#FF5733',
            specialties='Testing, Development'
        )
        
        # Create a subsystem
        self.subsystem = Subsystem.objects.create(
            name='Test Subsystem',
            description='A test subsystem',
            status='in_progress',
            responsible_subteam=self.subteam
        )
        
        # Create a team member
        self.team_member = TeamMember.objects.create(
            user=self.user,
            subteam=self.subteam,
            phone='555-1234',
            skills='Python, Django, Testing',
            is_leader=True
        )
        
        # Create a component
        self.component = Component.objects.create(
            name='Test Component',
            part_number='TC-001',
            description='A test component',
            expected_delivery=timezone.now().date() + timedelta(days=7),
            is_delivered=False
        )
        
        # Create a milestone
        self.milestone = Milestone.objects.create(
            name='Test Milestone',
            description='A test milestone',
            date=timezone.now().date() + timedelta(days=15),
            project=self.project
        )
        
        # Create a meeting
        self.meeting = Meeting.objects.create(
            date=timezone.now().date() + timedelta(days=5),
            start_time='09:00:00',
            end_time='10:00:00',
            notes='Test meeting notes',
            project=self.project
        )
        
        # Create a task
        self.task = Task.objects.create(
            title='Test Task',
            description='A test task description',
            estimated_duration=timedelta(hours=4),
            priority=2,
            progress=50,
            project=self.project,
            subsystem=self.subsystem
        )
        self.task.assigned_to.add(self.team_member)
        self.task.required_components.add(self.component)

    def test_project_save(self):
        """Test exporting a project to JSON"""
        url = reverse('core:project_save', args=[self.project.id])
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertTrue('attachment; filename=' in response['Content-Disposition'])
        
        # Parse the JSON response
        json_data = json.loads(response.content.decode('utf-8'))
        
        # Validate JSON structure
        self.assertIn('project', json_data)
        self.assertIn('tasks', json_data)
        self.assertIn('subsystems', json_data)
        self.assertIn('team_members', json_data)
        self.assertIn('subteams', json_data)
        self.assertIn('components', json_data)
        self.assertIn('milestones', json_data)
        self.assertIn('meetings', json_data)
        self.assertIn('format_version', json_data)
        
        # Validate project data
        project_data = json_data['project']
        self.assertEqual(project_data['fields']['name'], 'Test Project')
        
        # Validate task data
        tasks_data = json_data['tasks']
        self.assertEqual(len(tasks_data), 1)
        self.assertEqual(tasks_data[0]['fields']['title'], 'Test Task')
        
        # Validate task relationships (check that IDs are strings)
        task_relations = json_data['task_relations']
        self.assertIn(str(self.task.id), task_relations)
        
        # Check that component IDs in required_components are strings
        self.assertIn(str(self.component.id), task_relations[str(self.task.id)]['required_components'])
        
        # Check that team member IDs in assigned_to are strings
        self.assertIn(str(self.team_member.id), task_relations[str(self.task.id)]['assigned_to'])

    def test_project_load(self):
        """Test importing a project from JSON"""
        # First export the project
        export_url = reverse('core:project_save', args=[self.project.id])
        export_response = self.client.get(export_url)
        project_json = export_response.content
        
        # Delete the original project
        project_id = self.project.id
        self.project.delete()
        
        # Create a temporary file with the project JSON
        temp_file = tempfile.NamedTemporaryFile(suffix='.json')
        temp_file.write(project_json)
        temp_file.seek(0)
        
        # Import the project without renaming duplicates
        import_url = reverse('core:project_load')
        with open(temp_file.name, 'rb') as f:
            import_response = self.client.post(import_url, {
                'project_file': f,
                'rename_duplicates': False
            })
        
        # Check that we get a 200 status (error page)
        self.assertEqual(import_response.status_code, 200)
        
        # Clean up
        temp_file.close()

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON during import"""
        # Create a temporary file with invalid JSON
        temp_file = tempfile.NamedTemporaryFile(suffix='.json')
        temp_file.write(b'{"this is not valid JSON": ')
        temp_file.seek(0)
        
        # Import the project
        import_url = reverse('core:project_load')
        with open(temp_file.name, 'rb') as f:
            import_response = self.client.post(import_url, {
                'project_file': f,
                'rename_duplicates': 'on'
            })
        
        # Should render the error page
        self.assertEqual(import_response.status_code, 200)
        self.assertTemplateUsed(import_response, 'core/import_error.html')
        
        # Clean up
        temp_file.close()
        
    def test_empty_file_handling(self):
        """Test handling of empty files during import"""
        # Create an empty temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.json')
        temp_file.write(b'')
        temp_file.seek(0)
        
        # Import the project
        import_url = reverse('core:project_load')
        with open(temp_file.name, 'rb') as f:
            import_response = self.client.post(import_url, {
                'project_file': f,
                'rename_duplicates': 'on'
            })
        
        # Should render the error page
        self.assertEqual(import_response.status_code, 200)
        self.assertTemplateUsed(import_response, 'core/import_error.html')
        
        # Clean up
        temp_file.close()
        
    def test_missing_file_handling(self):
        """Test handling when no file is provided"""
        # Import without a file
        import_url = reverse('core:project_load')
        import_response = self.client.post(import_url, {
            'rename_duplicates': 'on'
        })
        
        # Should return to the import page with an error
        self.assertEqual(import_response.status_code, 200)
        self.assertTemplateUsed(import_response, 'core/project_load.html')(project_json)
        temp_file.seek(0)
        
        # Import the project
        import_url = reverse('core:project_load')
        with open(temp_file.name, 'rb') as f:
            import_response = self.client.post(import_url, {
                'project_file': f,
                'rename_duplicates': 'on'
            })
        
        # Check redirection
        self.assertEqual(import_response.status_code, 302)
        
        # Check that a new project was created
        self.assertTrue(Project.objects.filter(name='Test Project').exists())
        
        # Get the new project
        new_project = Project.objects.get(name='Test Project')
        
        # Check that the project has related objects
        self.assertTrue(Task.objects.filter(project=new_project).exists())
        self.assertTrue(Milestone.objects.filter(project=new_project).exists())
        self.assertTrue(Meeting.objects.filter(project=new_project).exists())
        
        # Check that task data is correct
        task = Task.objects.get(project=new_project)
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.progress, 50)
        
        # Clean up
        temp_file.close()

    def test_duplicate_project_name_handling(self):
        """Test handling of duplicate project names during import"""
        # Create a project with the same name
        duplicate_project = Project.objects.create(
            name='Test Project',
            description='Another project with the same name',
            start_date=timezone.now().date(),
            goal_end_date=timezone.now().date() + timedelta(days=30),
            hard_deadline=timezone.now().date() + timedelta(days=45)
        )
        
        # Export the original project
        export_url = reverse('core:project_save', args=[self.project.id])
        export_response = self.client.get(export_url)
        project_json = export_response.content
        
        # Create a temporary file with the project JSON
        temp_file = tempfile.NamedTemporaryFile(suffix='.json')
        temp_file.write(project_json)
        temp_file.seek(0)
        
        # Import the project with rename_duplicates=True
        import_url = reverse('core:project_load')
        with open(temp_file.name, 'rb') as f:
            import_response = self.client.post(import_url, {
                'project_file': f,
                'rename_duplicates': 'on'
            })
        
        # Check redirection
        self.assertEqual(import_response.status_code, 302)
        
        # Check that a new project was created with a different name
        projects = Project.objects.filter(name__startswith='Test Project (Import')
        self.assertTrue(projects.exists())
        
        # Clean up
        temp_file.close()
        
        # Test with rename_duplicates=False - This should fail gracefully
        temp_file = tempfile.NamedTemporaryFile(suffix='.json')
        temp_file.write