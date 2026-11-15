from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import Organization

from .models import UsageRecord


class UsageOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organization = Organization.objects.filter(memberships__user=request.user).first()
        if organization is None:
            return Response({"detail": "No organization found."}, status=status.HTTP_404_NOT_FOUND)
        records = UsageRecord.objects.filter(organization=organization)
        payload = {
            "total_requests": sum(r.request_count for r in records),
            "total_tokens": sum(r.token_count for r in records),
            "billable_requests": sum(r.request_count for r in records.filter(is_billable=True)),
        }
        return Response(payload, status=status.HTTP_200_OK)
