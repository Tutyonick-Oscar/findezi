from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views.index import DocumentTypeViewSet,LostDocViewSet,FoundDocViewSet

app_name = 'document'
router = DefaultRouter()
router.register(r'document/types',DocumentTypeViewSet, basename='document-types')
router.register(r'document/lost/report',LostDocViewSet, basename='document-lost-report')
router.register(r'document/found/report',FoundDocViewSet, basename='document-found-report')

urlpatterns = [
    path('',include(router.urls))
]