"""
Django settings for LeVeloRouge project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from decouple import config, Csv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PROJECT_DIR = os.path.abspath(os.path.dirname(__name__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJ_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)


# SECURITY WARNING: delete this code in production (maybe)
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         }
#     },
# }


ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'LVR.apps.LvrConfig',
    'corsheaders',
    'crispy_forms',
    'taggit',
    'pwa',
    'django_summernote'
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

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
    'http://localhost:9000',
]


CRISPY_TEMPLATE_PACK = 'bootstrap4'
GOOGLE_RECAPTCHA_SECRET_KEY = config('GOOGLE_RECAPTCHA_SECRET_KEY')


PWA_APP_NAME = 'Le velo rouge' 
PWA_APP_START_URL = '/' 
PWA_APP_SCOPE = '/' 
PWA_APP_DISPLAY = 'standalone' 
PWA_APP_BACKGROUND_COLOR = '#EBEBEB' 
PWA_APP_THEME_COLOR = '#F52B2B' 
PWA_APP_DESCRIPTION = "Le velo rouge - PWA" 
PWA_APP_DIR = 'ltr' 
PWA_APP_LANG = 'en-US'
PWA_APP_ORIENTATION = 'portrait-primary' 
PWA_APP_STATUS_BAR_COLOR = 'default' 


PWA_APP_ICONS = [ { 'src': '/static/LVR/assets/img/icons/r-icon.png', 'sizes': '160x160' }, { 'src': '/static/LVR/assets/img/icons/r-icon-192.png', 'sizes': '192x192' },  { 'src': '/static/LVR/assets/img/icons/r-icon-512.png', 'sizes': '512x512' } ] 
PWA_APP_ICONS_APPLE = [ { 'src': '/static/LVR/assets/img/icons/r-icon.png', 'sizes': '160x160' } ] 
PWA_APP_SPLASH_SCREEN = [ { 'src': '/static/LVR/assets/img/icons/splash-640x1136.png', 'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)' } ] 
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'LVR/static/LVR/assets/js/pwa', 'serviceworker.js')


ROOT_URLCONF = 'LeVeloRouge.urls'

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
                'LVR.ctxt_processors.searchPosts',
                'LVR.ctxt_processors.contactMsg',
                'LVR.ctxt_processors.newComment',
                'LVR.ctxt_processors.get_total_posts',
            ],
            # 'loaders': [
            #     ('django.template.loaders.cached.Loader', [
            #         'django.template.loaders.filesystem.Loader',
            #         'django.template.loaders.app_directories.Loader',
            #     ]),
            # ],
        },
    },
]

WSGI_APPLICATION = 'LeVeloRouge.wsgi.application'



# Email host server
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT', cast=int)




#Config & options for WYSIWYG Summernote editor
SUMMERNOTE_THEME = config('SUMMERNOTE_THEME')
X_FRAME_OPTIONS = config('X_FRAME_OPTIONS')

SUMMERNOTE_CONFIG = {
    'summernote': {
        'width': '99%',
        'height': '490',
    }
}



# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'CONN_MAX_AGE': 60 * 10, #10 minutes - This set the TTL (TimeToLive) database to 10 minutes, by default Django closses the conn after each query
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

from django.utils.translation import ugettext_lazy as _

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
)

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/



STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static') #For our project static
# ]



# STATIC_ROOT = 'D:/dojdsALLSTATICCOMPILED' #Where all our static will be copied
# More info about static and collectstatic in: https://www.youtube.com/watch?v=w9F9k-JHvcQ



# Media files (uploaded by any user, admin(s) or author)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')