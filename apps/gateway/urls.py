from django.urls import path

from .views import gateway_request

urlpatterns = [
    path("request/", gateway_request, name="gateway-request"),
]
