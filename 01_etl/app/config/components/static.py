"""Static files constants."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'

STATIC_ROOT = Path(BASE_DIR).joinpath('data', 'static')

MEDIA_URL = '/media/'

MEDIA_ROOT = Path(BASE_DIR).joinpath('data', 'media')

STATICFILES_DIRS = [] 
