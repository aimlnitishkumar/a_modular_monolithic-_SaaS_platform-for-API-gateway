from django.urls import path

from .views import AuditLogListAPIView

urlpatterns = [
    path("audit/", AuditLogListAPIView.as_view(), name="audit-log-list"),
]
