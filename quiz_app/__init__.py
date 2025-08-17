# src/quiz_app/__init__.py
"""
Quiz Application Package

A comprehensive quiz application with admin panel for managing questions
and taking timed quizzes with scoring and statistics.
"""

__version__ = "1.0.0"
__author__ = "Quiz App Team"
__email__ = "team@quizapp.com"
__description__ = "Interactive Quiz Application with Admin CRUD Panel"

# Package metadata
__all__ = [
    'models',
    'database', 
    'services',
    'gui',
    'utils',
    'config'
]

# Version info tuple
VERSION_INFO = (1, 0, 0)

def get_version():
    """Get version string."""
    return __version__

def get_app_info():
    """Get application information."""
    return {
        'name': 'Quiz Application',
        'version': __version__,
        'author': __author__,
        'description': __description__
    }

