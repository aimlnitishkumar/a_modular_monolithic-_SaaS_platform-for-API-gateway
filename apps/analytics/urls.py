from django.urls import path

from .views import AnalyticsOverviewAPIView

urlpatterns = [
    path("analytics/overview/", AnalyticsOverviewAPIView.as_view(), name="analytics-overview"),
]
