from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'goal_end_date', 'hard_deadline']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'goal_end_date': forms.DateInput(attrs={'type': 'date'}),
            'hard_deadline': forms.DateInput(attrs={'type': 'date'}),
        }