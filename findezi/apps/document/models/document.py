import auto_prefetch
from django.db import models
from django.utils.translation import gettext_lazy as _

from findezi.apps.core.models import BaseModel


class Document(BaseModel):

    class DocStatus(models.TextChoices):
        LOST = "L", (_("Lost"))
        FOUND = "F", (_("Found"))
        TAKEN = "T", (_("Taken"))

    doc_type = models.CharField(max_length=50)
    delivery_place = models.CharField(max_length=50)
    delivery_date = models.DateField()
    expiration_date = models.DateField()
    doc_ref_number = models.CharField(max_length=50)
    doc_name = models.CharField(max_length=120)
    doc_last_name = models.CharField(max_length=120)
    doc_nick_name = models.CharField(max_length=120, null=True, blank=True)
    doc_date_of_birth = models.DateField(null=True, blank=True)
    doc_place_of_birth = models.CharField(max_length=120, null=True, blank=True)
    doc_image_recto = models.ImageField(upload_to="docs/lost", null=True, blank=True)
    doc_image_verso = models.ImageField(upload_to="docs/lost", null=True, blank=True)
    doc_status = models.CharField(max_length=1, choices=DocStatus.choices)
    finding_commission = models.DecimalField(
        max_digits=16, decimal_places=3, blank=True
    )

    class Meta(BaseModel.Meta):
        abstract = True


class LostDocument(Document):
    last_remembering_place = models.CharField(max_length=120)
    picker_reward = models.TextField()
    loser_email = models.EmailField(max_length=120)
    loser_number = models.IntegerField()
    loser = auto_prefetch.ForeignKey(
        "insurance.Loser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lost_documents",
    )


class FoundDocument(Document):
    founded_at = models.CharField(max_length=120)
    picker_email = models.EmailField(max_length=120)
    picker_number = models.IntegerField()
