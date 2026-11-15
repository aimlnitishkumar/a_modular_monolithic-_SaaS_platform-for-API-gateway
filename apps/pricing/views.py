from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import Organization

from .models import PricingRule


class PricingRuleListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organization = Organization.objects.filter(memberships__user=request.user).first()
        if organization is None:
            return Response({"detail": "No organization found."}, status=status.HTTP_404_NOT_FOUND)
        rules = PricingRule.objects.filter(plan__subscriptions__organization=organization).distinct()
        payload = [{
            "id": str(rule.id),
            "plan_code": rule.plan.code,
            "metric": rule.metric,
            "unit_price": str(rule.unit_price),
            "free_quota": str(rule.free_quota),
        } for rule in rules]
        return Response(payload, status=status.HTTP_200_OK)
