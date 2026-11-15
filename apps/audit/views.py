from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import Organization

from .models import AuditLog


class AuditLogListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organization = Organization.objects.filter(memberships__user=request.user).first()
        if organization is None:
            return Response({"detail": "No organization found."}, status=status.HTTP_404_NOT_FOUND)
        logs = AuditLog.objects.filter(organization=organization).order_by("-created_at")[:20]
        return Response([
            {"action": log.action, "details": log.details, "created_at": log.created_at.isoformat()}
            for log in logs
        ], status=status.HTTP_200_OK)
