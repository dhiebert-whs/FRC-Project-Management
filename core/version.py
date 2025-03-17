"""
FRC Project Management System version information.
"""

VERSION = "0.5.0"
VERSION_NAME = "Build Season Beta"

def get_version():
    """Return the current version string."""
    return VERSION

def get_version_name():
    """Return the current version name."""
    return VERSION_NAME

def get_full_version():
    """Return the full version string with name."""
    return f"{VERSION} - {VERSION_NAME}"