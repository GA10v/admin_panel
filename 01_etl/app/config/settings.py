"""Django settings for "config" project."""

from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

include(
    # SECRET_KEY, DEBUG, ALLOWED_HOSTS, INTERNAL_IPS
    'components/security.py',
    # DATABASES, DEFAULT_AUTO_FIELD
    'components/database.py',
    # INSTALLED_APPS, MIDDLEWARE, ROOT_URLCONF, TEMPLATES, WSGI_APPLICATION
    'components/application.py',
    # AUTH_PASSWORD_VALIDATORS
    'components/pswd_validation.py',
    # LANGUAGE_CODE, LOCALE_PATHS, TIME_ZONE, USE_I18N, USE_TZ
    'components/localization.py',
    # BASE_DIR, STATIC_URL, STATIC_ROOT, MEDIA_ROOT, STATICFILES_DIRS
    'components/static.py',
    # LOGGING
    'components/log_settings.py',
)
