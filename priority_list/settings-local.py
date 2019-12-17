"""
Django settings for priority_list project on Heroku. For more info, see:
https://github.com/heroku/heroku-django-template

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from datetime import timedelta

from priority_list.settings import *

SECRET_KEY = "supersecret"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition

DEBUG_TOOLBAR_PATCH_SETTINGS = False

INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
    "corsheaders",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "list.util.csrf_header_middleware",
    # 'list.util.react_header_middleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.template.context_processors.request",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

GRAPHENE = {
    "SCHEMA": "priority_list.schema.schema",
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware",],
}

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_EXPIRATION_DELTA": timedelta(minutes=5),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=7),
}

# CORS_EXPOSE_HEADERS = ['X-CSRFToken']

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = ["http://localhost:3000"]

REACT_SUPER_SECRET_KEY = "supersupersecret"

# CSRF_TRUSTED_ORIGINS = ['http://localhost:3000/']
# SESSION_COOKIE_SAMESITE = None
