"""
Django settings for GYM_FITNESS_BACKEND project.
Updated for Maximum Security & Reliability.
"""

import os
from pathlib import Path
from datetime import timedelta
import sys # Logging ke liye zaroori

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================
# 🔐 SECURITY SETTINGS
# ==============================================
# Asli Secret Key Environment Variable se lenge
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-CHANGE-THIS-IN-PRODUCTION-!!!')

# Production me False hona chahiye
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# ==============================================
# 📦 INSTALLED APPS
# ==============================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # Local apps
    'fitness',
    'members',
    'payments',
    'reminders',
    'reports',
    'whatsapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static files speed
    'corsheaders.middleware.CorsMiddleware', # Mobile connection
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==============================================
# 🗄️ DATABASE (Auto-Switch: Local vs Render)
# ==============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production (Render) par PostgreSQL use karega
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )

# User Model
AUTH_USER_MODEL = 'fitness.User'

# ==============================================
# 📸 FILE UPLOAD SETTINGS (Fix for Large Images)
# ==============================================
# 10 MB Limit (High Quality Photos ke liye)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024 
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# ==============================================
# 🔐 PASSWORD VALIDATION
# ==============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================
# 🌍 INTERNATIONALIZATION
# ==============================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata' # India Time
USE_I18N = True
USE_TZ = True

# ==============================================
# 📂 STATIC & MEDIA FILES
# ==============================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================
# 🚀 REST FRAMEWORK
# ==============================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    # Date Format Fix
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}

# ==============================================
# 🔑 JWT SETTINGS
# ==============================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24), # 1 Day Login
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# ==============================================
# 🌐 CORS (Connection Fix for Mobile/Web)
# ==============================================
CORS_ALLOW_ALL_ORIGINS = True # Dev ke liye True, Prod me specific domain daal sakte hain
CORS_ALLOW_CREDENTIALS = True
# Specific Headers Allow karo taaki Mobile App block na ho
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ==============================================
# 🛡️ PRODUCTION SECURITY
# ==============================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True # Always use HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ==============================================
# 📜 LOGGING (THE DEBUGGER)
# ==============================================
# Ye setting Error 500 ka asli reason Console me dikhayegi
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR', # 500 Errors yahan print honge
            'propagate': False,
        },
    },
}

# Directories Create karo taaki error na aaye
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(STATIC_ROOT, exist_ok=True)