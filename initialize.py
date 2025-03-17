# initialize.py

"""
FRC Project Management System - Initialization Script

This script is run on first startup or when the executable is launched.
It ensures all required directories exist and templates are properly placed.
"""

import os
import sys
import shutil
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('frc_pm_init.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('frc_pm_init')

def initialize_project():
    """
    Initialize the project for first run.
    """
    logger.info("Starting FRC Project Management System initialization")
    
    # Get base directory - when packaged with PyInstaller it's different
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        base_dir = Path(sys._MEIPASS)
        app_dir = Path(os.path.dirname(sys.executable))
        logger.info(f"Running as packaged app. Base dir: {base_dir}, App dir: {app_dir}")
    else:
        # Running in development
        base_dir = Path(__file__).resolve().parent
        app_dir = base_dir
        logger.info(f"Running in development mode. Base dir: {base_dir}")
    
    # Import after setting paths
    try:
        from core.version import VERSION, VERSION_NAME
        logger.info(f"Current version: {VERSION} - {VERSION_NAME}")
    except ImportError:
        logger.error("Failed to import version information")
        VERSION = "0.5.0"
        VERSION_NAME = "Build Season Beta"
        
    # Fix authentication templates
    fix_auth_templates(base_dir)
    
    # Set up database if it doesn't exist
    setup_database(app_dir)
    
    logger.info("Initialization completed successfully")
    return True

def fix_auth_templates(base_dir):
    """
    Fix the authentication templates issue.
    """
    logger.info("Fixing authentication templates")
    
    # Paths for template directories
    template_dir = base_dir / "core" / "templates"
    registration_dir = template_dir / "registration"
    
    # Create registration directory if it doesn't exist
    if not registration_dir.exists():
        logger.info(f"Creating registration template directory: {registration_dir}")
        os.makedirs(registration_dir, exist_ok=True)
    
    # Check for existing registration templates in the incorrect location
    incorrect_path = template_dir / "core" / "registration"
    if incorrect_path.exists():
        logger.info(f"Found templates in incorrect location: {incorrect_path}")
        
        # Move each template file to the correct location
        for template_file in incorrect_path.glob("*.html"):
            dest_path = registration_dir / template_file.name
            if not dest_path.exists():
                logger.info(f"Copying {template_file.name} to correct location")
                shutil.copy2(template_file, dest_path)
    
    # Ensure login.html exists
    login_template = registration_dir / "login.html"
    if not login_template.exists():
        logger.info("Login template missing, creating it")
        
        # Check if we can find an existing login template anywhere
        for possible_login in [
            template_dir / "login.html",
            template_dir / "core" / "login.html",
            incorrect_path / "login.html"
        ]:
            if possible_login.exists():
                logger.info(f"Found login template at {possible_login}, copying")
                shutil.copy2(possible_login, login_template)
                break
        else:
            # No login template found, create one
            logger.info("Creating new login template")
            create_login_template(login_template)

def create_login_template(path):
    """
    Create a basic login template file.
    """
    content = """{% extends 'core/base.html' %}

{% block title %}Log In - FRC Project Management{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-6 offset-md-3">
        <div class="card">
            <div class="card-header">
                <h2>Log In</h2>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="id_username" class="form-label">Username</label>
                        <input type="text" name="username" class="form-control" id="id_username" autocomplete="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="id_password" class="form-label">Password</label>
                        <input type="password" name="password" class="form-control" id="id_password" autocomplete="current-password" required>
                    </div>
                    {% if form.errors %}
                        <div class="alert alert-danger">
                            Your username and password didn't match. Please try again.
                        </div>
                    {% endif %}
                    <div class="d-flex justify-content-between">
                        <a href="{% url 'password_reset' %}" class="btn btn-link">Forgot Password?</a>
                        <button type="submit" class="btn btn-primary">Log In</button>
                    </div>
                    <input type="hidden" name="next" value="{{ next }}">
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    with open(path, 'w') as f:
        f.write(content)
    logger.info(f"Created login template at {path}")

def setup_database(app_dir):
    """
    Set up the database if it doesn't exist.
    """
    db_path = app_dir / "db.sqlite3"
    
    if not db_path.exists():
        logger.info("Database not found, will be created on first run")
    else:
        logger.info(f"Database found at {db_path}")
    
    # Note: The actual database creation happens when Django runs migrations

if __name__ == "__main__":
    initialize_project()