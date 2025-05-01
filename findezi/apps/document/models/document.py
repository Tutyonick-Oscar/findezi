import auto_prefetch
from django.db import models
from django.utils.translation import gettext_lazy as _

from findezi.apps.core.models import BaseModel
from findezi.apps.core.utilities.mails import (
    send_claimed_doc_info_mail,
    send_found_document_mail,
    send_picked_up_doc_mail,
    send_validated_found_document_mail,
)

from ..managers.document import DocumentManager


class DocumentType(BaseModel):
    class LifeTimeUnitChoices(models.TextChoices):
        DAYS = "D", (_("Days"))
        WEEKS = "W", (_("Weeks"))
        MONTHS = "M", (_("Months"))
        YEARS = "Y", (_("Years"))

    class PriceCurrencyChoices(models.TextChoices):
        DOLLAR = (
            "D",
            "Dollar",
        )
        FRANC_BU = "B", "BIF"
        FRANC_CONGOLAIS = "C", "CDF"

    name = models.CharField(max_length=120, unique=True)
    finding_cost = models.DecimalField(max_digits=16, decimal_places=3)
    finding_commission = models.DecimalField(
        max_digits=16, decimal_places=3, blank=True
    )
    insurance_fees = models.DecimalField(max_digits=3, decimal_places=3)
    lifetime = models.PositiveIntegerField()
    lifetime_unit = models.CharField(
        max_length=1,
        choices=LifeTimeUnitChoices.choices,
        default=LifeTimeUnitChoices.YEARS,
    )
    price = models.DecimalField(max_digits=16, decimal_places=3)
    price_currency = models.CharField(
        max_length=3, choices=PriceCurrencyChoices.choices
    )

    class Meta(BaseModel.Meta):
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.name}"

    def days_lifetime(self):
        if self.lifetime_unit == DocumentType.LifeTimeUnitChoices.DAYS:
            return self.lifetime
        elif self.lifetime_unit == DocumentType.LifeTimeUnitChoices.WEEKS:
            return self.lifetime * 7
        elif self.lifetime_unit == DocumentType.LifeTimeUnitChoices.MONTHS:
            return self.lifetime * 30
        elif self.lifetime_unit == DocumentType.LifeTimeUnitChoices.YEARS:
            return self.lifetime * 365

    def get_days_lifetime(self):
        return self.lifetime * self.days_lifetime()


class Document(BaseModel):

    class DocStatus(models.TextChoices):
        LOST = "L", (_("Lost"))
        PICKED_UP = "P", (_("Picked_up"))
        FOUND = "F", (_("Found"))
        CLAIMED = "C", (_("Claimed"))
        TAKEN = "T", (_("Taken"))

    doc_type = auto_prefetch.ForeignKey(
        "document.DocumentType", on_delete=models.PROTECT, related_name="%(class)ss"
    )
    delivery_place = models.CharField(max_length=50, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    doc_ref_number = models.CharField(max_length=50)
    doc_name = models.CharField(max_length=120)
    doc_last_name = models.CharField(max_length=120)
    doc_nick_name = models.CharField(max_length=120, null=True, blank=True)
    doc_date_of_birth = models.DateField(null=True, blank=True)
    doc_place_of_birth = models.CharField(max_length=120, null=True, blank=True)
    doc_image_recto = models.ImageField(upload_to="docs/lost", null=True, blank=True)
    doc_image_verso = models.ImageField(upload_to="docs/lost", null=True, blank=True)
    doc_status = models.CharField(max_length=1, choices=DocStatus.choices)

    objects = DocumentManager()

    class Meta(BaseModel.Meta):
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["doc_type", "doc_name", "doc_last_name"],
                condition=models.Q(deleted_at=None),
                name="issued_%(class)ss",
                violation_error_message="this document has already been issued",
            ),
            models.UniqueConstraint(
                fields=("doc_ref_number",),
                condition=models.Q(deleted_at=None),
                name="unique_%(class)ss_ref_number",
                violation_error_message="a document with this ref number has already been issued",
            ),
        ]

    def __str__(self):
        return f"{self.doc_name} : {self.doc_ref_number}"

    # admin function
    def close_issue(self):
        self.doc_status = LostDocument.DocStatus.TAKEN
        self.save()


class LostDocument(Document):
    last_remembering_place = models.CharField(max_length=120, null=True, blank=True)
    picker_reward = models.TextField(null=True, blank=True)
    loser_email = models.EmailField(max_length=120)
    loser_number = models.IntegerField()
    loser_insurance = auto_prefetch.ForeignKey(
        "insurance.LostDocumentInsurance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lost_documents",
    )
    found_by = models.EmailField(max_length=120, null=True, blank=True)

    def report_found(self, email):
        self.found_by = email
        self.doc_status = LostDocument.DocStatus.PICKED_UP
        self.save()
        send_picked_up_doc_mail(email=email)
        send_found_document_mail(email=self.loser_email, doc_obj=self)

    # admin function
    def validate_found_report(self):
        self.doc_status = LostDocument.DocStatus.FOUND
        self.save()
        send_validated_found_document_mail(email=self.loser_email, doc_obj=self)


class FoundDocument(Document):
    founded_at = models.CharField(max_length=120, null=True, blank=True)
    picker_email = models.EmailField(max_length=120)
    picker_number = models.IntegerField()
    claimed_by = models.EmailField(max_length=120, null=True, blank=True)

    def claim_doc(self, email):
        self.claimed_by = email
        self.doc_status = FoundDocument.DocStatus.CLAIMED
        self.save()
        send_claimed_doc_info_mail(email=email, doc_obj=self)

    # admin function
    def validate_pickup(self):
        self.doc_status = FoundDocument.DocStatus.FOUND
        self.save()
