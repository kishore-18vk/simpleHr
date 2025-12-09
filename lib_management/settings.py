import os
from pathlib import Path
import dj_database_url  # Needed for Render database

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY KEY
# Using a default for local dev, but Render will use the env var if set
SECRET_KEY = os.environ.get("SECRET_KEY", "1htka**s9t)1+_22+@fbc(@%xo^puxssn_cmsgupu!9%b3-rjs")

# Debug mode (False on Render if you set the env var, True locally)
DEBUG = os.environ.get("DEBUG", "True") == "True"

# Allowed Hosts
# On Render, this will allow the app URL. Locally it allows localhost.
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")


# Installed apps
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',

    # Your apps
    'library',
    'employee',
    'holiday',
    'leaves',
    'recruitment',
    'dashboard',
    'attendance',
    'payroll',
    'onboarding',
    'assets',
    'settings_app',
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <--- ADDED: Critical for static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lib_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'lib_management.wsgi.application'

# DATABASE SETTINGS
# Logic: If 'DATABASE_URL' exists (Render), use it. Otherwise use local MySQL.
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get("DB_NAME", "library_db"),
            'USER': os.environ.get("DB_USER", "django_user"),
            'PASSWORD': os.environ.get("DB_PASSWORD", "Kishore@18"),
            'HOST': os.environ.get("DB_HOST", "localhost"),
            'PORT': os.environ.get("DB_PORT", "3306"),
        }
    }

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ADDED: This allows Render to serve your static files efficiently
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# JWT Authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True  # Useful for testing, but careful in production
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://vortex-hrms.netlify.app"
]