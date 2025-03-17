# run_app.py

import os
import sys
import logging
from pathlib import Path

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