from django.urls import path

from .views import UsageOverviewAPIView

urlpatterns = [
    path("usage/", UsageOverviewAPIView.as_view(), name="usage-overview"),
]
