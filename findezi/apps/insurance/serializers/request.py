from rest_framework import serializers

from findezi.apps.core.serializers import DynamicFieldsModelSerializer as dfms
from findezi.apps.document.models.document import LostDocument
from findezi.apps.document.serializers import DocumentSerializer, LostDocSerializer

from ..models import InsuranceRequest


class InsuranceRequestSerializer(dfms):
    issued_doc = LostDocSerializer(
        read_only=True, fields=DocumentSerializer.Meta.fields
    )
    request_status = serializers.SerializerMethodField()

    class Meta:
        model = InsuranceRequest
        fields = [
            "issued_doc",
            "insurance_expected_delay",
            "fees",
            "request_status",
            "valided_at",
            "authorized_at",
            "canceled_at",
            "rejected_at",
        ]

        extra_kwargs = {"fees": {"read_only": True}}

    def get_request_status(self, obj):
        return obj.get_request_status_display()


class CreateInsuranceRequestSerializer(serializers.ModelSerializer):
    issued_doc = serializers.PrimaryKeyRelatedField(
        queryset=LostDocument.objects.filter(
            doc_status__in=[
                LostDocument.DocStatus.LOST,
                LostDocument.DocStatus.PICKED_UP,
            ]
        )
    )

    class Meta:
        model = InsuranceRequest
        fields = [
            "issued_doc",
            "insurance_expected_delay",
            "fees",
        ]

    def validate(self, attrs):

        issued_doc = attrs.get("issued_doc", None)
        delay = attrs.get("insurance_expected_delay", 30)
        fees = InsuranceRequest.objects.get_insurance_fees(
            issued_doc=issued_doc, insurance_expected_delay=delay
        )
        attrs["fees"] = fees
        return attrs
