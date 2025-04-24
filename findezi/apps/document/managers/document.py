from django.apps import apps

from findezi.apps.core.models import BaseManager


class DocumentManager(BaseManager):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.exclude(doc_status="T")
