"""
Django development settings for SpriteTest.
"""

from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use simple static file storage in development (no manifest hashing)
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

# Django Debug Toolbar
import sys
_TESTING = 'test' in sys.argv
if not _TESTING:
    INSTALLED_APPS += ['debug_toolbar']  # noqa: F405
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405
INTERNAL_IPS = ['127.0.0.1']

# Email - Console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
