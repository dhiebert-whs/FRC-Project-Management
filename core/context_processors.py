# core/context_processors.py

from core.version import get_version, get_version_name, get_full_version

def version_context(request):
    """
    Context processor that adds version information to the template context.
    """
    return {
        'app_version': get_version(),
        'app_version_name': get_version_name(),
        'app_full_version': get_full_version(),
    }