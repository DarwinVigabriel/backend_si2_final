# apps.py
from django.apps import AppConfig

class CooperativaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cooperativa"

    def ready(self):
        from . import admin_campaigns  # noqa
