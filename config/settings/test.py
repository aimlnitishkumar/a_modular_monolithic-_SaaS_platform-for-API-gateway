import os

from .base import *

if os.getenv("METERFLOW_TEST_DATABASE", "sqlite3") == "sqlite3":
    DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "test_db.sqlite3"}
else:
    DATABASES["default"]["NAME"] = env("POSTGRES_DB", default="meterflow_test")
    DATABASES["default"]["HOST"] = env("POSTGRES_HOST", default="localhost")
    DATABASES["default"]["USER"] = env("POSTGRES_USER", default="meterflow")
    DATABASES["default"]["PASSWORD"] = env("POSTGRES_PASSWORD", default="meterflow")

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
