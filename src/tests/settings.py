import pathlib

BASE_DIR = pathlib.Path(__file__).parent

SECRET_KEY = "your-secret-key-for-testing"

DEBUG = True

INSTALLED_APPS = [
    "django_typst",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django_typst.TypstEngine",
        "NAME": "typst",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {
            "ROOT": None,
            "FONT_PATHS": [],
            "IGNORE_SYSTEM_FONTS": False,
            "PDF_STANDARD": "1.7",
            "PPI": None,
        },
    },
]
