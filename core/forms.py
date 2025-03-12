from django import forms
from .models import Project, Subteam, Task, Subsystem, Meeting, TeamMember

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'goal_end_date', 'hard_deadline']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'goal_end_date': forms.DateInput(attrs={'type': 'date'}),
            'hard_deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class SubteamForm(forms.ModelForm):
    class Meta:
        model = Subteam
        fields = ['name', 'color_code', 'specialties']
        widgets = {
            'color_code': forms.TextInput(attrs={'type': 'color'}),
            'specialties': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'color_code': 'Select a color for the subteam',
            'specialties': 'Enter comma-separated skills or focus areas of this subteam'
        }

class TaskForm(forms.ModelForm):
    estimated_duration_days = forms.IntegerField(min_value=0, initial=0, required=False, 
                                              help_text="Number of days")
    estimated_duration_hours = forms.IntegerField(min_value=0, max_value=23, initial=0, required=False,
                                               help_text="Number of hours (0-23)")
    estimated_duration_minutes = forms.IntegerField(min_value=0, max_value=59, initial=0, required=False,
                                                 help_text="Number of minutes (0-59)")
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'subsystem', 'priority', 'assigned_to', 
                  'pre_dependencies', 'required_components', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'assigned_to': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'pre_dependencies': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'required_components': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'pre_dependencies': 'Tasks that must be completed before this task can start',
            'required_components': 'Components needed for this task'
        }
    
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit choices to the current project
        if project:
            self.fields['subsystem'].queryset = Subsystem.objects.all()
            if self.instance.pk:
                self.fields['pre_dependencies'].queryset = Task.objects.filter(project=project).exclude(pk=self.instance.pk)
            else:
                self.fields['pre_dependencies'].queryset = Task.objects.filter(project=project)
        
        # If we're editing an existing task, populate the duration fields
        if self.instance.pk and self.instance.estimated_duration:
            total_seconds = self.instance.estimated_duration.total_seconds()
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            
            self.initial['estimated_duration_days'] = int(days)
            self.initial['estimated_duration_hours'] = int(hours)
            self.initial['estimated_duration_minutes'] = int(minutes)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate dates
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', "End date cannot be before start date")
        
        # Create duration from the day, hour, and minute fields
        days = cleaned_data.get('estimated_duration_days') or 0
        hours = cleaned_data.get('estimated_duration_hours') or 0
        minutes = cleaned_data.get('estimated_duration_minutes') or 0
        
        import datetime
        cleaned_data['estimated_duration'] = datetime.timedelta(
            days=days,
            hours=hours,
            minutes=minutes
        )
        
        return cleaned_data
    
class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['user', 'subteam', 'phone', 'skills', 'is_leader']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'skills': 'Enter comma-separated skills of this team member',
            'is_leader': 'Check if this member is a subteam leader'
        }

