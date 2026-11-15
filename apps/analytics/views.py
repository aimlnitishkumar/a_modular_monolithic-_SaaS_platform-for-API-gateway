from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import Organization

from .services import get_analytics_overview


class AnalyticsOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organization = Organization.objects.filter(memberships__user=request.user).first()
        if organization is None:
            return Response({"detail": "No organization found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(get_analytics_overview(organization.id), status=status.HTTP_200_OK)
