from django.urls import path

from .views import PricingRuleListAPIView

urlpatterns = [
    path("pricing/", PricingRuleListAPIView.as_view(), name="pricing-rules"),
]
