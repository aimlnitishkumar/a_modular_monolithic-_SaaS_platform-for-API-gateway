from django.urls import path

from .views import APIKeyDetailAPIView, APIKeyListCreateAPIView, APIKeyRotateAPIView

urlpatterns = [
    path("keys/", APIKeyListCreateAPIView.as_view(), name="api-key-list-create"),
    path("keys/<uuid:pk>/", APIKeyDetailAPIView.as_view(), name="api-key-detail"),
    path("keys/<uuid:pk>/rotate/", APIKeyRotateAPIView.as_view(), name="api-key-rotate"),
]
