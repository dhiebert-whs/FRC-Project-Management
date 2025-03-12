# FRC Project Management System

## 📋 Summary
The FRC Project Management System is a specialized Django-based web application designed to help FIRST Robotics Competition (FRC) teams efficiently manage their robot build season from kickoff to competition. It provides comprehensive tools for project planning, task tracking, team management, attendance monitoring, and progress visualization to help teams stay organized throughout their build season.

## 🔍 Detailed Overview
This project management tool was created specifically for the unique needs of FRC teams who operate under tight timelines with a defined kickoff and competition schedule. The system integrates project planning, task dependencies, team organization, and resource tracking into a cohesive platform that supports the entire robotics project lifecycle.

### Key Features:
- **Project Configuration**: Set up project timelines with kickoff dates, target completion dates, and competition deadlines
- **Task Management**: Create, assign, and track tasks with dependencies, resource requirements, and progress monitoring
- **Gantt Chart Visualization**: Interactive visual representation of project timeline and progress
- **Team Organization**: Manage team members, subteams, and skill assignments
- **Attendance Tracking**: Record and monitor meeting attendance with detailed statistics
- **Project Persistence**: Export and import project data for backups, sharing, and version control
- **Documentation**: Built-in user guide and developer documentation

## 💻 Usage and Functions

### Project Management
- Define project timelines aligned with FRC season milestones
- Track overall project progress with detailed statistics
- Export projects for backup or sharing with other teams

### Task Tracking
- Create hierarchical tasks with dependencies
- Assign tasks to team members based on skills and availability
- Monitor completion status and critical path

### Team Organization
- Create color-coded subteams (Programming, Mechanical, Electrical, etc.)
- Assign members to appropriate subteams
- Track member skills and leadership roles

### Attendance System
- Schedule team meetings
- Record attendance with arrival and departure times
- Generate attendance reports and statistics

### Visualization
- Interactive Gantt chart showing task timelines and dependencies
- Progress indicators for tasks and overall project
- Critical path highlighting

### Data Preservation
- Export complete project data to portable JSON files
- Import project data from previously exported files
- Maintain project history through regular exports

## 🚀 Future Development Plans

The following enhancements are planned for future releases:

### API Development (Priority: Medium)
- RESTful API endpoints for mobile app integration
- API documentation for developers

### Advanced Analytics (Priority: Medium)
- Team performance metrics and dashboards
- Project progress forecasting
- Resource allocation optimization

### Windows Executable Enhancements (Priority: Medium)
- First-run setup wizard for database initialization
- Version checking and update mechanism
- Improved static files handling for better performance
- Reduced executable size through dependency optimization

### Integration Features (Priority: Low)
- CAD software integration for component tracking
- Version control system integration
- Calendar/scheduling tool integration

### UI Improvements (Priority: Low)
- Mobile-responsive design enhancements
- Dark mode theme
- Customizable dashboard layout

### Security Enhancements (Priority: Low)
- Enhanced authentication mechanisms
- Role-based permissions
- Audit logging
- Data encryption for sensitive information

## 📥 Installation

### Web Application Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/frc-project-management.git
   cd frc-project-management
   ```

2. **Environment Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Run migrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   ```

4. **Running the Server**
   ```bash
   python manage.py runserver
   ```
   
   Access at http://localhost:8000/

### Standalone Windows Executable

1. **Download the Latest Release**
   - Go to the Releases page and download the latest `FRC_Project_Management.zip`
   - Extract the contents to a location of your choice

2. **Run the Application**
   - Double-click `FRC_Project_Management.exe`
   - The first time you run it, the application will:
     - Create a new SQLite database
     - Prompt you to create an admin account
   - Access the application at http://localhost:8000/ in your browser

3. **Notes**
   - Do not move the executable after first run (database is stored relative to its location)
   - Create regular backups using the built-in project export feature
   - For security, use this application only on your local network

### Building from Source
To build the Windows executable yourself:

1. **Install Requirements**
   ```bash
   pip install pyinstaller waitress
   ```

2. **Create Spec File**
   Create a file named `frc_project_management.spec` with the content provided in the documentation.

3. **Build Executable**
   ```bash
   pyinstaller frc_project_management.spec
   ```

4. **Distribute**
   The executable will be created in the `dist` folder.

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.