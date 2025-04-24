from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import HybridImageField
from rest_framework import serializers

from findezi.apps.core.serializers import DynamicFieldsModelSerializer as dfms

from .models.document import DocumentType, FoundDocument, LostDocument


class DocTypeSerializer(dfms):

    class Meta:
        model = DocumentType
        fields = [
            "id",
            "name",
            "finding_cost",
            "finding_commission",
        ]


class DocumentSerializer(serializers.Serializer):

    doc_type = serializers.SlugRelatedField(
        slug_field="name", queryset=DocumentType.objects.all()
    )
    doc_image_recto = HybridImageField(required=False)  # TODO required
    doc_image_verso = HybridImageField(required=False)  # TODO required
    doc_status = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "id",
            "doc_type",
            "delivery_place",
            "delivery_date",
            "expiration_date",
            "doc_ref_number",
            "doc_name",
            "doc_last_name",
            "doc_nick_name",
            "doc_date_of_birth",
            "doc_place_of_birth",
            "doc_image_recto",
            "doc_image_verso",
            "doc_status",
            "created_at",
        ]

    def get_doc_status(self, obj):
        return obj.get_doc_status_display()


class LostDocSerializer(DocumentSerializer, dfms):

    class Meta(DocumentSerializer.Meta):
        model = LostDocument
        default_fields = DocumentSerializer.Meta.fields
        fields = default_fields + [
            "last_remembering_place",
            "picker_reward",
            "loser_email",
            "loser_number",
        ]

        extra_kwargs = {
            "loser_email": {"write_only": True},
            "loser_number": {"write_only": True},
        }

    def validate(self, attrs):
        try:
            FoundDocument.objects.get(
                doc_type=attrs.get("doc_type", None),
                doc_name=attrs.get("doc_name", None),
                doc_last_name=attrs.get("doc_last_name", None),
                doc_ref_number=attrs.get("doc_ref_number", None),
            )
            raise ValidationError(
                _("this document has already been issued, is it yours ?")
            )
        except FoundDocument.DoesNotExist:
            return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)


class FoundDocSerializer(DocumentSerializer, dfms):

    class Meta(DocumentSerializer.Meta):
        model = FoundDocument
        default_fields = DocumentSerializer.Meta.fields
        fields = default_fields + [
            "founded_at",
            "picker_email",
            "picker_number",
        ]

        extra_kwargs = {
            "picker_email": {"write_only": True},
            "picker_number": {"write_only": True},
        }

    def validate(self, attrs):
        try:
            LostDocument.objects.get(
                doc_type=attrs.get("doc_type", None),
                doc_name=attrs.get("doc_name", None),
                doc_last_name=attrs.get("doc_last_name", None),
                doc_ref_number=attrs.get("doc_ref_number", None),
            )
            raise ValidationError(
                _("this document has already been issued, have you find it ?")
            )
        except LostDocument.DoesNotExist:
            return attrs

    def create(self, validated_data):
        return super().create(validated_data)
