"""
Django settings for Aartcy project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# ENVIRON
import environ

root = environ.Path(__file__)
env = environ.Env()
environ.Env.read_env(env_file='.env')

# CLIENT_URL = env.str('CLIENT_URL')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.list('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
# ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'channels',
    'rest_framework',
    'rest_framework.authtoken',
    'settings',
    'accounts',
    'payments.apps.PaymentsConfig',
    'analytics',
    'arts.apps.ArtsConfig',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Aartcy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'Aartcy.wsgi.application'
ASGI_APPLICATION = "sockets.routing.application"  # Socket Server

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': env.db()
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
CORS_ORIGIN_WHITELIST = env.tuple('CORS_ORIGIN_WHITELIST')
# CORS_ORIGIN_WHITELIST = [
#     "http://localhost:4200",
#     "http://127.0.0.1:4200"
# ]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = env.str('STATIC_ROOT')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Django Rest Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    "DATE_INPUT_FORMATS": ["%m/%d/%Y"],
    "DATETIME_FORMAT": "%m/%d/%Y %I:%M:%S %p" + " " + TIME_ZONE,
}

# Email Settings
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')

# Stripe Settings
if DEBUG is True:
    # if development mode, DOMAIN should be localhost:4200
    STRIPE_SECRET_KEY = 'sk_test_VmrihYzMQmS7XmDU5fYFcCej00uknEsOVg'
    STRIPE_PUBLISHABLE_KEY = 'pk_test_HT6HE4tJf7H35fM7UgxPU27e00kLYmwnkL'
    STRIPE_CLIENT_ID = 'ca_Gy5W5loNkI2u8JKlsgVk4RXyPeh3gt4N'
else:
    # if production mode, DOMAIN should be arttwork.com
    STRIPE_SECRET_KEY = env.str('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = env.str('STRIPE_PUBLISHABLE_KEY')
    STRIPE_CLIENT_ID = env.str('STRIPE_CLIENT_ID')


if DEBUG is True:
    # if development mode, DOMAIN should be localhost:4200
    DOMAIN = "http://localhost:4200"
else:
    # if production mode, DOMAIN should be arttwork.com
    DOMAIN = "https://" + ALLOWED_HOSTS[0]

PAGE_LIMIT = 10
PAGE_OFFSET = 1

# Django Socket Layers
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}

# SOCIAL APP
GOOGLE_CLIENT_ID = env.str('GOOGLE_CLIENT_ID')
TWITTER_CONSUMER_API_KEY = env.str('TWITTER_CONSUMER_API_KEY')
TWITTER_CONSUMER_API_SEC_KEY = env.str('TWITTER_CONSUMER_API_SEC_KEY')
