"""
Django settings for ansibleapi project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import logging
from configparser import ConfigParser

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#!uqjo-gdxn#baf)cpn$y_68muu&4)ij&ywm*ac8_2#b5%$u3o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


if DEBUG:
    # will output to your console
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(module)s %(levelname)s %(message)s',
    )
else:
    # will output to logging file
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(module)s %(levelname)s %(message)s',
        filename = 'debug.log',
        filemode = 'a'
    )

ALLOWED_HOSTS = ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'api',
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

ROOT_URLCONF = 'ansibleapi.urls'

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

WSGI_APPLICATION = 'ansibleapi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

# ANSIBLE MODULE ALLOW
MODULE = ["shell", "command"]

# TASK FOR RUN CELERY
TASKS_HANDLERS = {
    "MODULEAPI": {
        "BACKEND": "ansibleapi.ansibleapi.tasks.tasks.ExecuteAnsibleModuleAPI"
    }

}

DEV_SETTINGS_FILE = os.getenv("POLEMARCH_DEV_SETTINGS_FILE",
                              os.path.join(BASE_DIR, 'main/settings.ini'))

config = ConfigParser()
config.read([DEV_SETTINGS_FILE])

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600
}
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/3'
CELERY_WORKER_CONCURRENCY = config.getint("rpc", "concurrency", fallback=4)
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_BROKER_HEARTBEAT = config.getint("rpc", "heartbeat", fallback=10)
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_EXPIRES = config.getint("rpc", "results_expiry_days", fallback=10)
CELERY_TIME_ZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

SECRET_KEY = 'sdfsfFKLJodsg082343223_'