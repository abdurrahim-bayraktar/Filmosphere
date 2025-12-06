import os
from pathlib import Path

import environ

env = environ.Env(
    DJANGO_DEBUG=(bool, True),
)

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env")) if os.path.exists(
    os.path.join(BASE_DIR, ".env")
) else None

SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-secret-key")

DEBUG = env.bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS: list[str] = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "corsheaders",
    "rest_framework_simplejwt",
    "core",
    "films",
    "api",
    "users",
]

SITE_ID = 1

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "filmosphere.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "filmosphere.wsgi.application"
ASGI_APPLICATION = "filmosphere.asgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://filmouser:filmopass@localhost:5432/filmosphere",
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Filmosphere API",
    "DESCRIPTION": "Film search and aggregation microservice.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

IMDBAPI_BASE = env("IMDBAPI_BASE", default="https://api.imdbapi.dev")
KINO_BASE = env("KINO_BASE", default="https://api.kinocheck.com")
KINO_API_KEY = env("KINO_API_KEY", default="")
WATCHMODE_BASE = env("WATCHMODE_BASE", default="https://api.watchmode.com/v1")
WATCHMODE_API_KEY = env("WATCHMODE_API_KEY", default="")
DEEPSEEK_API_KEY = env("DEEPSEEK_API_KEY", default="")
DEEPSEEK_BASE = env("DEEPSEEK_BASE", default="https://api.deepseek.com/v1")
CACHE_TTL_HOURS = env.int("CACHE_TTL_HOURS", default=24)
HTTP_TIMEOUT = env.int("HTTP_TIMEOUT", default=10)
HTTP_RETRIES = env.int("HTTP_RETRIES", default=3)

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

CORS_ALLOW_CREDENTIALS = True

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}

# Comment Moderation Settings
COMMENT_BLACKLIST = [
    # Add blacklisted words/phrases here
    # Example: "spam", "scam", etc.
    # Can be overridden via environment variable
]
COMMENT_BLACKLIST = env.list("COMMENT_BLACKLIST", default=COMMENT_BLACKLIST)


