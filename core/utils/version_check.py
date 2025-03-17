# core/utils/version_check.py

import json
import urllib.request
from urllib.error import URLError
from packaging import version

from core.version import VERSION

def check_for_updates(timeout=5):
    """
    Check if there's a newer version available.
    
    Args:
        timeout: Timeout in seconds for the HTTP request
        
    Returns:
        dict: Contains update information with keys:
            - 'update_available': Boolean indicating if an update is available
            - 'latest_version': String with the latest version number
            - 'download_url': URL to download the latest version
            - 'error': Error message if the check failed, None otherwise
    """
    result = {
        'update_available': False,
        'latest_version': VERSION,
        'download_url': None,
        'error': None
    }
    
    try:
        # This URL would need to be replaced with your actual version check endpoint
        url = 'https://frc-project-management-updates.example.com/api/version'
        
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request, timeout=timeout)
        
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            
            latest_version = data.get('latest_version', '0.0.0')
            current_version = VERSION
            
            if version.parse(latest_version) > version.parse(current_version):
                result['update_available'] = True
                result['latest_version'] = latest_version
                result['download_url'] = data.get('download_url')
                
    except URLError as e:
        result['error'] = f"Connection error: {str(e)}"
    except json.JSONDecodeError:
        result['error'] = "Invalid response from server"
    except Exception as e:
        result['error'] = f"Error checking for updates: {str(e)}"
        
    return result