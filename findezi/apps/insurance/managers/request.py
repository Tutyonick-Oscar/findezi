from datetime import timedelta

from django.apps import apps
from django.utils import timezone

from findezi.apps.config.utilities import currency_exchange
from findezi.apps.core.models import BaseManager


class InsuranceRequestManager(BaseManager):

    def authorize_request_(self, request, admin):
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

    def get_insurance_fees(self, issued_doc, insurance_expected_delay=30):
        doc_type = issued_doc.doc_type
        print(doc_type)
        fees = doc_type.get_insurance_fees(delay=insurance_expected_delay)
        return fees
