from django.urls import path

from .views import SubscriptionCreateAPIView, SubscriptionCurrentAPIView

urlpatterns = [
    path("subscriptions/", SubscriptionCreateAPIView.as_view(), name="subscription-create"),
    path("subscriptions/current/", SubscriptionCurrentAPIView.as_view(), name="subscription-current"),
]
