from django.utils.translation import gettext as _
from rest_framework import mixins, permissions, response, status
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from findezi.apps.core.permissions.main import IsOwner
from findezi.apps.core.utilities import codes

from ..serializers.request import (
    CreateInsuranceRequestSerializer,
    InsuranceRequest,
    InsuranceRequestSerializer,
)


class InsuranceRequestViewSet(ModelViewSet):
    serializer_class = InsuranceRequestSerializer
    queryset = InsuranceRequest.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateInsuranceRequestSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return response.Response(
            {
                "success": True,
                "response_code": codes.API_SUCCESS,
                "response_data": self.serializer_class(instance).data,
                "response_message": _("insurance requested succefully"),
            },
            status=status.HTTP_201_CREATED,
        )
