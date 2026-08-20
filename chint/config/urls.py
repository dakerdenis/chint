from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from web.views.health import health_check

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/", include("api.urls")),
    path("api-test2/", include("api_test2.urls")),
    path("", RedirectView.as_view(url="/en/", permanent=False)),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("web.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
