"""
Production settings for Filmosphere
"""
import os
from .settings import *

# Security
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Database - using SQLite for simplicity (can upgrade to PostgreSQL later)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# CORS - Update this with your frontend URL after deployment
CORS_ALLOW_ALL_ORIGINS = True  # Change this in production
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if os.environ.get('CORS_ALLOWED_ORIGINS') else []

# Security settings
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'

# External API Keys (set these in Render environment variables)
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
WATCHMODE_API_KEY = os.environ.get('WATCHMODE_API_KEY', '')
KINO_API_KEY = os.environ.get('KINO_API_KEY', 'fCxG8kroiDIHzQZWXnhJ0NVdqwqtmahDz0OSnCieTMEwTlj6vj37Bs4KFbcaYmlv')

