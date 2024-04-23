"""
Django settings for VotingSystem project - Development Settings.
"""

from .base import *
import logging

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DEV_DB_NAME'),
        'USER': config('DEV_DB_USER'),
        'PASSWORD': config('DEV_DB_PASSWORD'),
        'HOST': config('DEV_DB_HOST'),
        'PORT': config('DEV_DB_PORT'),
    }
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)