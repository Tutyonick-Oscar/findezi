from django.urls import include, path, re_path

from findezi.utils import app_path

urlpatterns = [
    path("accounts/", include(f"{app_path('authentication')}.urls.api")),
    path("", include(f"{app_path('document')}.urls")),
    path("", include(f"{app_path('insurance')}.urls")),
]
