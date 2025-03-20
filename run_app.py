import os
import sys
import logging
from pathlib import Path
from waitress import serve

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

# Import Django settings and start server
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
    # Import Django modules AFTER the settings are configured
    from django.core.management import call_command
    import django
    django.setup()
    
    from core.version import VERSION, VERSION_NAME
    logger.info(f"FRC Project Management System v{VERSION} - {VERSION_NAME}")
    print(f"FRC Project Management System v{VERSION} - {VERSION_NAME}")
    
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
    
    # Determine port
    PORT = int(os.environ.get('PORT', 8000))
    
    # Start Waitress server
    logger.info(f"Starting server on port {PORT}")
    print(f"Starting server on port {PORT}")
    print(f"\n* Access the application at http://localhost:{PORT}")
    print("* Press Ctrl+C to stop the server")
    
    serve(application, host='127.0.0.1', port=PORT)
    
except Exception as e:
    logger.error(f"Error starting application: {str(e)}")
    print(f"Error starting application: {str(e)}")
    input("Press Enter to exit...")
    sys.exit(1)