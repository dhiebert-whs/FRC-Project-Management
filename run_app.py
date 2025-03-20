#initialize()
import os
import sys
from waitress import serve
from django.core.wsgi import get_wsgi_application

# Ensure proper path handling for both development and frozen environments
if getattr(sys, 'frozen', False):
    # When running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
    # Add BASE_DIR to path so Python can find your modules
    sys.path.insert(0, BASE_DIR)
    
    # Print to aid in debugging
    print(f"Running in frozen mode. BASE_DIR: {BASE_DIR}")
    
    # Also print the available directories/files to help debug
    print("\nAvailable directories and files:")
    for root, dirs, files in os.walk(BASE_DIR, topdown=False):
        for name in dirs:
            if "templates" in name:
                print(os.path.join(root, name))
else:
    # In development
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"Running in development mode. BASE_DIR: {BASE_DIR}")

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frc_project_management.settings')

# Initialize Django
application = get_wsgi_application()

# Run waitress server
if __name__ == '__main__':
    # Import Django modules AFTER the settings are configured
    from django.core.management import call_command
    import django
    django.setup()
    
    print("\n==== FRC Project Management System ====")
    print("\nChecking database...")
    
    # Run migrations automatically
    try:
        print("Setting up database (running migrations)...")
        call_command('migrate', interactive=False)
        print("Database migrations complete!")
        
        # Check if we need to create a superuser
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("\nNo admin account found. Let's create one:")
            username = input("Username (default: admin): ") or "admin"
            from getpass import getpass
            password = getpass("Password (input will be hidden): ")
            email = input("Email (optional): ")
            
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"Admin user '{username}' created successfully!")
    except Exception as e:
        print(f"Error during database setup: {str(e)}")
        print("Please run migrations manually with: python manage.py migrate")
    
    print("\nStarting server...")
    print("\n* Access the application at: http://localhost:8000")
    print("* Press Ctrl+C to stop the server")
    
    #waitress.serve(application, host='127.0.0.1', port=8000)
    serve(application, host='127.0.0.1', port=8000)