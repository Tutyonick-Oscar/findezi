from django.contrib import admin

from .models.document import DocumentType, FoundDocument, LostDocument


@admin.action(description="Validate Pickup")
def validate_pickup(modeladmin, request, queryset):
    for document in queryset.all():
        document.validate_pickup()


@admin.action(description="Validate Found Report")
def validate_found_report(modeladmin, request, queryset):
    for document in queryset.all():
        document.validate_found_report()


@admin.action(description="Close Issue")
def close_issue(modeladmin, request, queryset):
    for document in queryset.all():
        document.close_issue()


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "finding_cost",
        "finding_commission",
        "created_by__username",
        "insurance_fees",
        "lifetime",
        "lifetime_unit",
        "price",
        "price_currency",
    ]


@admin.register(FoundDocument)
class FoundDocumentAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            doc_status__in=[
                FoundDocument.DocStatus.PICKED_UP,
                FoundDocument.DocStatus.CLAIMED,
            ]
        )

    list_display = [
        "doc_type__name",
        "delivery_place",
        "delivery_date",
        "expiration_date",
        "doc_ref_number",
        "doc_status",
        "doc_name",
        "doc_last_name",
        "doc_nick_name",
        "doc_date_of_birth",
        "doc_place_of_birth",
        "doc_image_recto",
        "doc_image_verso",
        "founded_at",
        "picker_email",
        "picker_number",
        "claimed_by",
    ]

    search_fields = ["doc_name", "doc_last_name", "doc_ref_number"]
    list_filter = ["doc_status"]
    actions = [validate_pickup, close_issue]


@admin.register(LostDocument)
class LostDocumentAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            doc_status__in=[
                LostDocument.DocStatus.PICKED_UP,
                LostDocument.DocStatus.LOST,
            ]
        )

    list_display = [
        "doc_type__name",
        "delivery_place",
        "delivery_date",
        "expiration_date",
        "doc_ref_number",
        "doc_status",
        "doc_name",
        "doc_last_name",
        "doc_nick_name",
        "doc_date_of_birth",
        "doc_place_of_birth",
        "doc_image_recto",
        "doc_image_verso",
        "loser_email",
        "loser_number",
        "found_by",
        "last_remembering_place",
        "picker_reward",
    ]

    search_fields = ["doc_name", "doc_last_name", "doc_ref_number"]
    list_filter = ["doc_status"]
    actions = [validate_found_report, close_issue]
