from datetime import timedelta

from django.apps import apps
from django.utils import timezone

from findezi.apps.core.models import BaseManager


class InsuranceRequestManager(BaseManager):

    def authorize_request_(request, admin):
        LostDocumentInsurance = apps.get_model("insurance", "LostDocumentInsurance")
        insurance_start_date = timezone.now().date()
        new_insurance = LostDocumentInsurance(
            insurance_start_date=insurance_start_date,
            insurance_end_date=insurance_start_date
            + timedelta(days=request.insurance_expected_delay),
            request=request,
            insurance_fees=request.fees,
        )
        new_insurance.save()
        return new_insurance
