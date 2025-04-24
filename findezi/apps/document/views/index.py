from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from findezi.apps.core.utilities import codes
from findezi.apps.core.utilities.mails import send_picked_up_doc_mail

from ..serializers import (
    DocTypeSerializer,
    DocumentType,
    FoundDocSerializer,
    FoundDocument,
    LostDocSerializer,
    LostDocument,
)


class DocumentTypeViewSet(GenericViewSet, ListModelMixin):
    serializer_class = DocTypeSerializer
    queryset = DocumentType.objects.all()


class LostDocViewSet(
    GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin
):
    serializer_class = LostDocSerializer
    queryset = LostDocument.objects.exclude(
        doc_status__in=[LostDocument.DocStatus.FOUND, LostDocument.DocStatus.PICKED_UP]
    )  # TODO we can't report et picked up document, this list must be filtered
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(doc_status=LostDocument.DocStatus.LOST)
        return Response(
            {
                "success": True,
                "response_code": codes.API_SUCCESS,
                "response_data": serializer.data,
                "response_message": _("document loss reported succefully"),
            },
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["post"], detail=True)
    def report_found(self, request, pk):
        email = request.data.get("email", None)
        if email is None:
            user = request.user
            if isinstance(user, get_user_model()):
                email = user.email
            else:
                return Response(
                    {
                        "success": False,
                        "response_code": codes.API_GENERIC_ERROR,
                        "response_data": None,
                        "response_message": _(
                            "you must either login or provide the email data"
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        instance = self.get_object()
        instance.report_found(email=email)

        return Response(
            {
                "success": True,
                "response_code": codes.API_SUCCESS,
                "response_data": None,
                "response_message": _(
                    "document found reported, check you mail box for more informations"
                ),
            },
            status=status.HTTP_202_ACCEPTED,
        )


class FoundDocViewSet(
    GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin
):
    serializer_class = FoundDocSerializer
    queryset = FoundDocument.objects.filter(
        doc_status=FoundDocument.DocStatus.FOUND
    )  # TODO we can't claim et not found document, this list must be filtered
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(doc_status=FoundDocument.DocStatus.PICKED_UP)
        send_picked_up_doc_mail(email=instance.picker_email)
        return Response(
            {
                "success": True,
                "response_code": codes.API_SUCCESS,
                "response_data": serializer.data,
                "response_message": _("document found reported succefully"),
            },
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["post"], detail=True)
    def claim_doc(self, request, pk):
        email = request.data.get("email", None)
        if email is None:
            user = request.user
            if isinstance(user, get_user_model()):
                email = user.email
            else:
                return Response(
                    {
                        "success": False,
                        "response_code": codes.API_GENERIC_ERROR,
                        "response_data": None,
                        "response_message": _(
                            "you must either login or provide the email data"
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        instance = self.get_object()
        instance.claim_doc(email=email)

        return Response(
            {
                "success": True,
                "response_code": codes.API_SUCCESS,
                "response_data": None,
                "response_message": _(
                    "document claimed, check you mail box for more informations"
                ),
            },
            status=status.HTTP_202_ACCEPTED,
        )
