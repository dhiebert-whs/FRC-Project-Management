#initialize()
import os
import sys
import logging
from pathlib import Path
from waitress import serve
from django.core.wsgi import get_wsgi_application

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('frc_pm.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('frc_pm')

'''
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
'''
# Configure paths for frozen app vs. development
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    base_dir = Path(sys._MEIPASS)
    app_dir = Path(os.path.dirname(sys.executable))
    logger.info(f"Running as packaged app. Base dir: {base_dir}, App dir: {app_dir}")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'frc_project_management.settings'
    sys.path.insert(0, str(base_dir))
else:
    # Running in development
    base_dir = Path(__file__).resolve().parent
    app_dir = base_dir
    logger.info(f"Running in development mode. Base dir: {base_dir}")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'frc_project_management.settings'

# Import and run initialization
try:
    from initialize import initialize_project
    initialize_project()
except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    print(f"Error during initialization: {str(e)}")

'''
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
    '''

# Import Django settings and start server
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
    from core.version import VERSION, VERSION_NAME
    logger.info(f"FRC Project Management System v{VERSION} - {VERSION_NAME}")
    print(f"FRC Project Management System v{VERSION} - {VERSION_NAME}")
    
    # Determine port
    PORT = int(os.environ.get('PORT', 8000))
    
    # Start Waitress server
    logger.info(f"Starting server on port {PORT}")
    print(f"Starting server on port {PORT}")
    print(f"Access the application at http://localhost:{PORT}")
    
    from waitress import serve
    serve(application, host='0.0.0.0', port=PORT)
    
except Exception as e:
    logger.error(f"Error starting application: {str(e)}")
    print(f"Error starting application: {str(e)}")
    input("Press Enter to exit...")
    sys.exit(1)