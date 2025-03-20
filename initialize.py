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
        
    # Fix template structure first
    fix_template_structure(base_dir)

    # Fix authentication templates
    fix_auth_templates(base_dir)

    # Fix static files including JavaScript
    fix_static_files(base_dir, app_dir)
    
    # Set up database if it doesn't exist
    setup_database(app_dir)
    
    logger.info("Initialization completed successfully")
    return True

def fix_template_structure(base_dir):
    """
    Ensure all templates are in the correct locations in the templates directory structure.
    """
    logger.info("Fixing template directory structure")
    
    # Define paths
    template_dir = base_dir / "core" / "templates"
    core_template_dir = template_dir / "core"
    
    # Ensure core template directory exists
    os.makedirs(core_template_dir, exist_ok=True)
    
    # Check if base.html is in the wrong location
    base_template = template_dir / "base.html"
    target_base_template = core_template_dir / "base.html"
    
    templates_fixed = False
    
    if base_template.exists() and not target_base_template.exists():
        logger.info(f"Copying base.html to correct location: {target_base_template}")
        shutil.copy2(base_template, target_base_template)
        templates_fixed = True
    
    # Check for other template files that should be in core/ directory
    for template_file in template_dir.glob("*.html"):
        # Skip registration directory files
        if template_file.name != "base.html" and "registration" not in str(template_file):
            target_file = core_template_dir / template_file.name
            if not target_file.exists():
                logger.info(f"Copying {template_file.name} to core/ directory")
                shutil.copy2(template_file, target_file)
                templates_fixed = True
    
    logger.info(f"Template structure fix {'applied' if templates_fixed else 'not needed'}")
    return templates_fixed

def fix_static_files(base_dir, app_dir):
    """
    Ensure static files, including JavaScript, are properly copied and available.
    """
    logger.info("Checking static files (JS, CSS)")
    
    # Define paths for static files
    source_static_dir = base_dir / "static"
    target_static_dir = app_dir / "static"
    
    # Create the target directory if it doesn't exist
    os.makedirs(target_static_dir, exist_ok=True)
    
    # Check if js directory exists and create it if needed
    source_js_dir = source_static_dir / "js"
    target_js_dir = target_static_dir / "js"
    
    if source_js_dir.exists() and not target_js_dir.exists():
        os.makedirs(target_js_dir, exist_ok=True)
        
        # Copy all JS files
        for js_file in source_js_dir.glob("*.js"):
            target_file = target_js_dir / js_file.name
            if not target_file.exists():
                logger.info(f"Copying JS file: {js_file.name}")
                shutil.copy2(js_file, target_file)
    
    # Similar process for CSS files
    source_css_dir = source_static_dir / "css"
    target_css_dir = target_static_dir / "css"
    
    if source_css_dir.exists() and not target_css_dir.exists():
        os.makedirs(target_css_dir, exist_ok=True)
        
        # Copy all CSS files
        for css_file in source_css_dir.glob("*.css"):
            target_file = target_css_dir / css_file.name
            if not target_file.exists():
                logger.info(f"Copying CSS file: {css_file.name}")
                shutil.copy2(css_file, target_file)
    
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
                        <a href="{{ request.GET.next|default:'/' }}" class="btn btn-secondary">Cancel</a>
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