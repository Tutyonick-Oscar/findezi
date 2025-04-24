from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

admin.site.site_title = "FINDEZI"
admin.site.site_header = "FINDEZI ADMIN"
admin.site.index_title = "FINDEZI ADMIN"

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path("api/", include("findezi.routes.api")),
    # re_path("web/", include("findezi.routes.web")),
]

# spectacular
urlpatterns += [
    path("api/docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
