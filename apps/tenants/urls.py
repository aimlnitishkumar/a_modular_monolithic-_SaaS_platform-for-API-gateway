from django.urls import path

from .views import OrganizationListCreateAPIView

urlpatterns = [
    path("organizations/", OrganizationListCreateAPIView.as_view(), name="organization-list-create"),
]
