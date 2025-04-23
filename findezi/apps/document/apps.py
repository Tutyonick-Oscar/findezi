from django.apps import AppConfig

from findezi.utils import app_path


class DocumentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = app_path("document")
