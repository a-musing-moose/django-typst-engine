import pathlib

BASE_DIR = pathlib.Path(__file__).parent

SECRET_KEY = "your-secret-key-for-testing"

DEBUG = True

INSTALLED_APPS = [
    "django_typst",
    "tests.test_app",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

TEMPLATES = [
    # A Default is always expected
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,
    },
    {
        "BACKEND": "django_typst.TypstTemplate",
        "NAME": "typst",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "ROOT": None,
            "FONT_PATHS": [],
            "IGNORE_SYSTEM_FONTS": False,
            "PDF_STANDARD": "1.7",
            "PPI": None,
        },
    },
]
