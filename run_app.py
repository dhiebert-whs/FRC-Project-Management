import os
import sys
import waitress
from django.core.wsgi import get_wsgi_application

# Ensure proper path handling for both development and frozen environments
if getattr(sys, 'frozen', False):
    # When running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
    sys.path.insert(0, BASE_DIR)
else:
    # In development
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frc_project_management.settings')

# Initialize Django
application = get_wsgi_application()

# Run waitress server
if __name__ == '__main__':
    from django import setup
    setup()
    
    # Create database if it doesn't exist
    from django.core.management import call_command
    
    print("\n==== FRC Project Management System ====")
    print("\nChecking database...")
    
    # Check if we need to run migrations
    import django.db
    try:
        django.db.connection.cursor()
        # If no error, database exists
        print("Database connected successfully!")
    except django.db.OperationalError:
        print("Setting up database for first run...")
        call_command('migrate')
        print("Database setup complete!")
        
        # Create a superuser if none exists
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("\nNo admin account found. Let's create one:")
            username = input("Username (default: admin): ") or "admin"
            from getpass import getpass
            password = getpass("Password (input will be hidden): ")
            email = input("Email (optional): ")
            
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"Admin user '{username}' created successfully!")
    
    print("\nStarting server...")
    print("\n* Access the application at: http://localhost:8000")
    print("* Press Ctrl+C to stop the server")
    
    waitress.serve(application, host='127.0.0.1', port=8000)