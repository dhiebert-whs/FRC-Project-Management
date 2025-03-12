# FRC Project Management System User Guide

## Introduction

Welcome to the FRC Project Management System! This platform is designed specifically for FIRST Robotics Competition (FRC) teams to manage their build season effectively from kickoff through competition. This guide will walk you through all the features and functionality of the system.

## Getting Started

### Accessing the System

1. Open your web browser and navigate to the application URL
2. Log in with your username and password
3. If you don't have an account, contact your team's system administrator

### Dashboard Overview

The Dashboard is your home base and provides:
- A quick overview of all your projects
- Recent activity across your projects
- Quick links to common actions

## Project Management

### Creating a New Project

1. From the Dashboard or Projects page, click the "+ New Project" button
2. Fill in the required project details:
   - **Name**: A descriptive name for your project
   - **Description**: A brief overview of the project's purpose
   - **Start Date**: When the project begins (usually kickoff)
   - **Goal End Date**: When you aim to complete the project
   - **Hard Deadline**: The absolute final deadline (competition date)
3. Click "Save Project" to create your new project

### Managing Existing Projects

For each project, you can:
- **View Details**: See all information about the project
- **Edit**: Update project information
- **Delete**: Remove a project (use with caution)
- **Export**: Save the project to a file for backup or sharing
- **Import**: Load a previously exported project

### Project Export and Import

#### Exporting a Project

1. Navigate to the project you want to export
2. Click the "Save to File" or "Export" button
3. The project will be downloaded as a JSON file to your computer

#### Importing a Project

1. From the Projects page, click "Import Project"
2. Select a JSON file previously exported from the system
3. Choose whether to automatically rename the project if a duplicate name exists
4. Click "Import Project" to load the project into the system

## Task Management

### Creating Tasks

1. From a project's detail page, click "+ Add Task"
2. Enter the task details:
   - **Title**: Clear, descriptive name
   - **Description**: What needs to be done
   - **Subsystem**: Which part of the robot this relates to
   - **Estimated Duration**: How long you expect it to take
   - **Priority**: Importance of the task
   - **Start/End Dates**: When work should begin and end
   - **Dependencies**: Tasks that must be completed first
   - **Required Components**: Parts needed for the task
   - **Assigned Team Members**: Who will work on this task
3. Click "Save Task" to create the task

### Viewing and Updating Tasks

1. Click on any task to view its details
2. Use the progress slider to update completion percentage
3. Click "Mark Complete" when the task is finished
4. Edit any task details as needed with the "Edit" button

## Team Management

### Subteams

Organize your team into functional groups:

1. From the navigation menu, click "Subteams"
2. Create a new subteam with the "+ New Subteam" button
3. Assign a name, color code, and specialties to each subteam

### Team Members

1. From the navigation menu, click "Team Members"
2. Add new team members with the "+ Add Team Member" button
3. For each member, record:
   - User account information
   - Contact details
   - Subteam assignment
   - Skills
   - Leadership status

## Meetings and Attendance

### Scheduling Meetings

1. From a project page, navigate to "Meetings"
2. Click "+ Schedule Meeting"
3. Enter meeting details:
   - Date
   - Start and end times
   - Notes or agenda

### Recording Attendance

1. From the meeting details page, click "Record Attendance"
2. Mark each team member as present or absent
3. For present members, record arrival and departure times
4. Click "Save Attendance" to store the information

## Gantt Chart Visualization

The Gantt chart provides a visual timeline of your project:

1. From a project page, click "View Gantt Chart"
2. Use the view buttons to organize tasks by:
   - Subsystem
   - Subteam
   - Team Member
3. Export the chart as an SVG file for presentations or documentation

## Daily Operations

### Daily Task View

1. Use the daily view to see what needs to be done in each meeting
2. Update task progress as work is completed
3. Reassign tasks if team members are absent

## Tips for Success

1. **Regular Updates**: Keep task progress updated during each meeting
2. **Dependencies**: Make sure to set proper task dependencies for accurate scheduling
3. **Attendance**: Track attendance consistently for better resource planning
4. **Documentation**: Use notes fields to document decisions and changes
5. **Backups**: Export projects regularly for backup and version control

## Troubleshooting

### Common Issues

1. **Can't import a project file**:
   - Ensure the file is a valid JSON file exported from this system
   - Check that the file isn't corrupted

2. **Tasks showing incorrect dependencies**:
   - Review and update the pre-dependencies in the task edit screen

3. **Team member doesn't appear in assignment list**:
   - Verify the team member has been properly added to the system

For additional support, contact your system administrator or refer to the developer documentation.