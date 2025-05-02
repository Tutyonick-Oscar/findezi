from django.apps import AppConfig

from findezi.utils import app_path


class ConfigConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = app_path("config")
