import auto_prefetch
from django.contrib.auth import get_user_model
from django.db import models

from findezi.apps.core.models import BaseModel

User = get_user_model()


class Loser(BaseModel):
    created_by = auto_prefetch.OneToOneField(
        User, on_delete=models.CASCADE, related_name="loser"
    )
    insurance_start_date = models.DateField(auto_now_add=True)
    insurance_end_date = models.DateField(blank=True)


class InsuranceCard(BaseModel):
    loser = auto_prefetch.ForeignKey(
        Loser, on_delete=models.CASCADE, related_name="insurance_cards"
    )
    issued_doc = auto_prefetch.OneToOneField(
        "document.LostDocument", on_delete=models.PROTECT, related_name="insurance_card"
    )
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    card_unique_code = models.CharField(max_length=50, unique=True, blank=True)
    card_image_file = models.FileField(
        null=True, blank=True, upload_to="insurance_cards"
    )
    card_qr_code_image = models.ImageField(
        null=True, blank=True, upload_to="insurance_cards_qr_codes"
    )
