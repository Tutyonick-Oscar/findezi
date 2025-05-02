from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.request import InsuranceRequestViewSet

router = DefaultRouter()
app_name = "insurance"
router.register(
    r"insurance/requests", InsuranceRequestViewSet, basename="insurance-request"
)

urlpatterns = [path("", include(router.urls))]
