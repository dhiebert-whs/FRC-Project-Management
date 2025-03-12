# Project Persistence: User Guide

## Introduction

The Project Persistence feature allows you to export your FRC Project Management projects to files and import them back later. This is useful for:

- Creating project backups
- Sharing project templates with other teams
- Transferring projects between different installations
- Creating different versions of a project

## Exporting a Project

Exporting a project saves all its data to a JSON file that can be stored on your computer.

### How to Export a Project:

1. From the Projects List:
   - Navigate to the Projects list page
   - Find the project you want to export
   - Click the "Export" button on the project card

2. From the Project Detail Page:
   - Open the project you want to export
   - Click the "Save to File" button in the top-right corner

3. After clicking the export button:
   - Your browser will download a JSON file named after your project
   - The file will contain all project data, including tasks, dependencies, team members, and settings

### What Gets Exported:

- Project details (name, description, dates)
- All tasks and their dependencies
- Subsystems
- Team members and subteams
- Components and resources
- Milestones and meetings
- Attendance records

## Importing a Project

Importing allows you to load a previously exported project file back into the system.

### How to Import a Project:

1. Go to the Projects list page
2. Click the "Import Project" button in the top-right corner
3. In the Import Project page:
   - Click "Choose File" to select your project JSON file
   - Check the "Automatically rename" box if you want to avoid name conflicts
   - Click "Import Project"
4. Wait for the import to complete
5. You'll be redirected to the new project's detail page

### Import Options:

- **Automatic Renaming**: If checked, the system will automatically rename imported projects if a project with the same name already exists. For example, "Robot Arm" might become "Robot Arm (Import 1)".

### Handling Duplicates:

When importing a project, the system attempts to match existing entities:

- **Subteams**: Matched by name
- **Components**: Matched by name and part number
- **Team Members**: Matched by associated user account
- **Subsystems**: Matched by name

Matching entities will be reused rather than creating duplicates.

## Troubleshooting

### Import Errors:

If the import fails, you'll see an error page with details about what went wrong. Common issues include:

- **Invalid JSON format**: The file might be corrupted or not a valid JSON file
- **Incompatible format**: The file might not be a valid project export or was created with a different version of the system
- **Missing dependencies**: Some required elements might be missing

### Large Projects:

- Large projects with many tasks and dependencies may take longer to export/import
- A progress indicator will show during the import process

## Best Practices

1. **Regular backups**: Export important projects regularly to prevent data loss
2. **Version naming**: Use descriptive names for different versions of your projects (e.g., "Robot Arm 2025 - Planning Phase")
3. **Template sharing**: Create template projects with common subsystems and export them for reuse
4. **Documentation**: Note what changes were made between different exported versions

## Technical Details

- Project files are in JSON format and can be viewed in any text editor
- Files contain a "format_version" field to track compatibility
- The import process uses transactions to ensure all-or-nothing imports
- Project relationships (like task dependencies) are preserved during import/export