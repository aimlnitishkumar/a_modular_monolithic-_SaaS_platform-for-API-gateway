from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def healthz(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz, name="healthz"),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.tenants.urls")),
    path("api/v1/", include("apps.api_keys.urls")),
    path("api/v1/", include("apps.subscriptions.urls")),
    path("api/v1/", include("apps.pricing.urls")),
    path("api/v1/", include("apps.usage.urls")),
    path("api/v1/", include("apps.billing.urls")),
    path("api/v1/", include("apps.analytics.urls")),
    path("api/v1/", include("apps.audit.urls")),
    path("gateway/v1/", include("apps.gateway.urls")),
]
