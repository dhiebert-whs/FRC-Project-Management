import os
import sys
import waitress
from django.core.wsgi import get_wsgi_application

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frc_project_management.settings')

# Initialize Django
application = get_wsgi_application()

# Run waitress server
if __name__ == '__main__':
    print("Starting FRC Project Management System...")
    print("Open your browser and navigate to http://localhost:8000")
    waitress.serve(application, host='127.0.0.1', port=8000)