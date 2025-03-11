from django.contrib import admin
from .models import (
    Subteam, TeamMember, Subsystem, Project, 
    Component, Task, Meeting, Attendance, Milestone
)

admin.site.register(Subteam)
admin.site.register(TeamMember)
admin.site.register(Subsystem)
admin.site.register(Project)
admin.site.register(Component)
admin.site.register(Task)
admin.site.register(Meeting)
admin.site.register(Attendance)
admin.site.register(Milestone)