"""
Django settings for VotingSystem project - Production Settings.
"""

from .base import *

DEBUG = False

ALLOWED_HOSTS = ['localhost']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# Static files
STATIC_ROOT = BASE_DIR / 'static'