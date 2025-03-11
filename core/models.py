from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import datetime

class Subteam(models.Model):
    name = models.CharField(max_length=100)
    color_code = models.CharField(max_length=7)  # Hex color code
    specialties = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subteam = models.ForeignKey(Subteam, on_delete=models.SET_NULL, null=True, related_name='members')
    phone = models.CharField(max_length=15, blank=True)
    skills = models.TextField(blank=True)
    is_leader = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Subsystem(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('testing', 'Testing'),
        ('issues', 'Issues'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    responsible_subteam = models.ForeignKey(Subteam, on_delete=models.SET_NULL, null=True, related_name='subsystems')
    
    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    goal_end_date = models.DateField()
    hard_deadline = models.DateField()
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Component(models.Model):
    name = models.CharField(max_length=255)
    part_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    expected_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Task(models.Model):
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    estimated_duration = models.DurationField(help_text="Format: days hours:minutes:seconds")
    actual_duration = models.DurationField(null=True, blank=True)
    assigned_to = models.ManyToManyField(TeamMember, blank=True, related_name='assigned_tasks')
    subsystem = models.ForeignKey(Subsystem, on_delete=models.CASCADE, related_name='tasks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    pre_dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='post_dependencies')
    required_components = models.ManyToManyField(Component, blank=True, related_name='required_for_tasks')
    progress = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class Meeting(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='meetings')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Meeting on {self.date} ({self.start_time}-{self.end_time})"

class Attendance(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendances')
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='attendances')
    present = models.BooleanField(default=False)
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('meeting', 'member')
    
    def __str__(self):
        status = "Present" if self.present else "Absent"
        return f"{self.member} - {status} at {self.meeting}"

class Milestone(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    
    def __str__(self):
        return self.name