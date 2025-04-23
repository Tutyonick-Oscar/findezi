from django.contrib import admin
from .models.document import DocumentType


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'finding_cost',
        'finding_commission',
        'created_by__username',
    ]

