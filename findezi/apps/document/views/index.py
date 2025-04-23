from ..serializers import DocumentType,DocTypeSerializer,LostDocSerializer,FoundDocSerializer,FoundDocument,LostDocument
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin,CreateModelMixin,RetrieveModelMixin
from rest_framework import status
from rest_framework.response import Response
from findezi.apps.core.utilities import codes
from django.utils.translation import gettext_lazy as _


class DocumentTypeViewSet(GenericViewSet,ListModelMixin):
    serializer_class = DocTypeSerializer
    queryset = DocumentType.objects.all()
    
class LostDocViewSet(GenericViewSet,ListModelMixin,CreateModelMixin,RetrieveModelMixin):
    serializer_class = LostDocSerializer
    queryset = LostDocument.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            doc_status = LostDocument.DocStatus.LOST
        )
        return Response(
            {
            "success": True,
            "response_code": codes.API_SUCCESS,
            "response_data": serializer.data,
            "response_message": _("document issued succefully"),
        },
        status=status.HTTP_201_CREATED,
        )
        
class FoundDocViewSet(GenericViewSet,ListModelMixin,CreateModelMixin,RetrieveModelMixin):
    serializer_class = FoundDocSerializer
    queryset = FoundDocument.objects.all()
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            doc_status = FoundDocument.DocStatus.FOUND
        )
        return Response(
            {
            "success": True,
            "response_code": codes.API_SUCCESS,
            "response_data": serializer.data,
            "response_message": _("document issued succefully"),
        },
        status=status.HTTP_201_CREATED,
        )