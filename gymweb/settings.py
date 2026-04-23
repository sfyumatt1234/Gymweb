"""
Django settings for the gymweb project.

Local-first body composition + workout tracker.
Database: MySQL (default) with a SQLite fallback for quick local dev.

Environment loading
-------------------
We look for env files in this order and use the first one that exists:
    1. .env.local   (git-ignored, personal dev overrides)
    2. .env         (shared template / production values)

Both short names (SECRET_KEY, DEBUG, ALLOWED_HOSTS, ...) and DJANGO_* names
are accepted so .env.local files from other tooling "just work".
"""

from pathlib import Path

from decouple import Config, RepositoryEnv, config as _default_config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_config():
    for name in (".env.local", ".env"):
        candidate = BASE_DIR / name
        if candidate.exists():
            return Config(RepositoryEnv(str(candidate)))
    return _default_config


config = _load_config()


def _cfg(*keys, default=None, cast=None):
    """Return the first env var found among ``keys`` (falls back to ``default``).

    We intentionally read the raw value first so that the ``cast`` callable
    is never applied to our internal sentinel.
    """
    sentinel = object()
    for key in keys:
        raw = config(key, default=sentinel)
        if raw is not sentinel:
            return cast(raw) if cast is not None else raw
    return default


SECRET_KEY = _cfg(
    "DJANGO_SECRET_KEY",
    "SECRET_KEY",
    default="django-insecure-change-me-in-production-please-0p^5w@^=c",
)

DEBUG = _cfg("DJANGO_DEBUG", "DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = _cfg(
    "DJANGO_ALLOWED_HOSTS",
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost,0.0.0.0,test.gigxmatch.com",
    cast=Csv(),
)
if "test.gigxmatch.com" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = list(ALLOWED_HOSTS) + ["test.gigxmatch.com"]

CSRF_TRUSTED_ORIGINS = _cfg(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "CSRF_TRUSTED_ORIGINS",
    default=(
        "http://127.0.0.1:5174,"
        "http://localhost:5174,"
        "http://test.gigxmatch.com:5174"
    ),
    cast=Csv(),
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tracker",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gymweb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "gymweb.wsgi.application"


# Database configuration.
# DB_ENGINE can be "mysql" (default) or "sqlite" for a quick start.
DB_ENGINE = _cfg("DB_ENGINE", default="mysql").lower()

if DB_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": _cfg("DB_NAME", default="gymweb"),
            "USER": _cfg("DB_USER", default="root"),
            "PASSWORD": _cfg("DB_PASSWORD", default=""),
            "HOST": _cfg("DB_HOST", default="127.0.0.1"),
            "PORT": _cfg("DB_PORT", default="3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = _cfg("DJANGO_TIME_ZONE", "TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/admin/login/"
