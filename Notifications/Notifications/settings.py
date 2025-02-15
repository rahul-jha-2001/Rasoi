"""
Django settings for Notifications project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
import sys
from pathlib import Path
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '{asctime} {levelname} [{name}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/notifications.log',
            'formatter': 'detailed',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed'
        },
        'kafka_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/kafka_consumer.log',
            'formatter': 'simple',
        },
        'worker_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/worker.log',
            'formatter': 'simple',
        },  
        'kafka_console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'grpc_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/grpc_service.log',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'kafka_consumer': {
            'handlers': ['kafka_file', 'kafka_console'],
            'level': 'INFO',
            'propagate': False,
        },
        'worker': {
            'handlers': ['worker_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'grpc_service': {
            'handlers': ['grpc_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}


# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Setup basic logging for settings initialization


# Add all directories in project root to Python path
# Skip common directories that shouldn't be in path
SKIP_DIRS = {
    '__pycache__',
    'venv',
    'env',
    '.git',
    '.idea',
    '.vscode',
    'logs',
    'media',
    'static',
    'migrations',
}

# Get all directories in BASE_DIR
for item in BASE_DIR.iterdir():
    if item.is_dir() and item.name not in SKIP_DIRS:
        sys.path.append(str(item))

# Print added paths for debugging
# print("Python path additions:")
# for path in sys.path:
#     if str(BASE_DIR) in path:
#         print(f"- {path}")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+7uunn5^7za+@du97w^$u_rd=4x2u5lgk(4hiq$#%hz&kvloh5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'template',
    'message_service',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Notifications.urls'

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

WSGI_APPLICATION = 'Notifications.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


WHATSAPP_BUSINESS_ACCOUNT_ID = "529193380271872"
WHATSAPP_PHONE_NUMBER_ID = "485021908033854"
WHATSAPP_ACCESS_TOKEN = "EAAIKPl0JQMUBO9zdcHxqlqTRKuj1TKxA82L4IbfQkF645HkFSSw5UdaptYNZCGVTN8t3sanbMOkZCW4PiKBVy6Ie05jg6mO5m26LrzQiYM2VSCnLgNXkZChIqekjbELFjtebXEHHflZAZBNL6DdGKGtzZCMKJBU7CXAP50vZBQtJEEe771yCQZBZBfFpPbyInLsG2b54kTsg1ewnXSPCtqCQ824cYWIfonegn28DZC8GbH"
WHATSAPP_API_URL = "https://graph.facebook.com/v21.0"

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
