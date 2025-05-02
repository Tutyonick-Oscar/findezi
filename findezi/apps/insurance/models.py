import auto_prefetch
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from findezi.apps.core.models import BaseModel

from .managers.request import InsuranceRequestManager

User = get_user_model()


class LostDocumentInsurance(BaseModel):
    class InsuranceStatus(models.TextChoices):
        ACTIVE = "A", (_("Active"))
        CANCELLED = "C", (_("Cancelled"))
        EXPIRED = "E", (_("Expired"))

    insurance_start_date = models.DateField(auto_now_add=True)
    insurance_end_date = models.DateField(blank=True)
    insurance_status = models.CharField(
        max_length=1, choices=InsuranceStatus.choices, default=InsuranceStatus.ACTIVE
    )
    request = auto_prefetch.OneToOneField(
        "InsuranceRequest", on_delete=models.PROTECT, related_name="doc_insurance"
    )
    insurance_fees = models.DecimalField(max_digits=16, decimal_places=3)


class InsuranceCard(BaseModel):
    lost_doc_insurance = auto_prefetch.OneToOneField(
        "LostDocumentInsurance",
        on_delete=models.CASCADE,
        related_name="card",
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
    is_active = models.BooleanField(default=True)


class InsuranceRequest(BaseModel):
    class RequestStatus(models.TextChoices):
        PENDING = "P", (_("Pending"))
        VALIDATED = "V", (_("Validated"))
        CANCELLED = "C", (_("Cancelled"))
        REJECTED = "R", (_("Rejected"))
        AUTHORIZED = "A", (_("Authorized"))

    issued_doc = auto_prefetch.OneToOneField(
        "document.LostDocument",
        on_delete=models.PROTECT,
        related_name="insurance_request",
    )
    insurance_expected_delay = models.PositiveIntegerField(default=30)
    fees = models.DecimalField(max_digits=16, decimal_places=3, blank=True)
    request_status = models.CharField(
        max_length=1, choices=RequestStatus.choices, default=RequestStatus.PENDING
    )
    # this should be an hr or admin instance
    validated_by = auto_prefetch.ForeignKey(
        "authentication.User",
        related_name="insurances_validated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    valided_at = models.DateTimeField(null=True, blank=True)
    # this should be an hr or admin instance
    authorized_by = auto_prefetch.ForeignKey(
        "authentication.User",
        related_name="insurances_granted",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    authorized_at = models.DateTimeField(null=True, blank=True)
    canceled_by = auto_prefetch.ForeignKey(
        "authentication.User",
        related_name="insurances_cancelled",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    canceled_at = models.DateTimeField(null=True, blank=True)
    rejected_by = auto_prefetch.ForeignKey(
        "authentication.User",
        related_name="insurances_rejected",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    rejected_at = models.DateTimeField(null=True, blank=True)

    objects = InsuranceRequestManager()

    class Meta(BaseModel.Meta):
        ordering = ("created_at",)

    def __str__(self):
        return f"request n°{self.pk}"

    def is_validated(self):
        return self.validated_by and self.valided_at

    def is_canceled(self):
        return self.canceled_by and self.canceled_at

    def is_rejected(self):
        return self.rejected_by and self.rejected_at

    def is_authorized(self):
        return self.authorized_by and self.authorized_at

    def is_pending(self):
        return (
            not self.is_canceled()
            and not self.is_rejected()
            and not self.is_authorized()
        )

    def is_cancelable(self):
        return (
            # not self.is_validated() and
            not self.is_rejected()
            and not self.is_canceled()
        )

    def is_rejectable(self):
        return (
            not self.is_rejected()
            and not self.is_canceled()
            and not self.is_authorized()
        )

    def is_authorizable(self):
        if self.is_validated():
            return True
        return False

    def can_be_validated(self):
        if self.is_pending():
            return True
        return False

    # admin function
    def cancel_request(self, admin):
        if self.is_cancelable():
            if isinstance(User, admin) and admin.is_superuser:
                self.canceled_by = admin
                self.canceled_at = timezone.now()
                self.request_status = InsuranceRequest.RequestStatus.CANCELLED
                self.save()
                return True, _("Request canceled successfully.")
            else:
                return False, _(
                    "The request cancelation must be done by an admin only."
                )
        return False, _("Request could not be canceled.")

    # admin function
    def validate_request(self, admin):
        if not self.can_be_validated():
            return False, _("This object seems already validated or rejected.")
        if isinstance(User, admin) and admin.is_superuser:
            self.validated_by = admin
            self.valided_at = timezone.now()
            self.request_status = InsuranceRequest.RequestStatus.VALIDATED
            self.save()
            return True, _("Request validated successfully.")
        else:
            return False, _("The request validation must be done by an admin only.")

    # admin function
    def reject_request(self, admin):
        if not self.is_rejectable():
            return False, _(
                "This object seems already validated,authorized or rejected."
            )
        if isinstance(User, admin) and admin.is_superuser:
            self.rejected_by = admin
            self.rejected_at = timezone.now()
            self.request_status = InsuranceRequest.RequestStatus.REJECTED
            self.save()
            return True, _("Request rejected successfully.")
        else:
            return False, _("The request rejection must be done by an admin only.")

    # admin function

    def authorize_request(self, admin):
        if not self.is_authorizable():
            return False, _("The object must be validated first.")

        if isinstance(User, admin) and admin.is_superuser:
            insurance = self.__class__.objects.authorize_request_(
                request=self, admin=admin
            )
            self.authorized_by = admin
            self.authorized_at = timezone.now()
            self.request_status = InsuranceRequest.RequestStatus.AUTHORIZED
            self.save()

        return insurance
