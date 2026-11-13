from .settings import *  # noqa: F403


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Las migraciones de catálogo parten de registros importados desde el SQL base;
# para las pruebas unitarias, genera el esquema directamente desde los modelos.
MIGRATION_MODULES = {"core": None}
