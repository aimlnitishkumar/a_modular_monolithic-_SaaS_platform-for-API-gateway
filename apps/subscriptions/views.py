from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import Membership, Organization

from .models import Subscription, SubscriptionPlan
from .services import ensure_subscription_for_organization


class SubscriptionCurrentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organization = Organization.objects.filter(memberships__user=request.user).first()
        if organization is None:
            return Response({"detail": "No organization found."}, status=status.HTTP_404_NOT_FOUND)
        subscription = Subscription.objects.filter(organization=organization).select_related("plan").first()
        if subscription is None:
            subscription = ensure_subscription_for_organization(organization=organization, created_by=request.user)
        return Response({
            "organization_id": str(organization.id),
            "plan_code": subscription.plan.code,
            "status": subscription.status,
            "monthly_request_limit": subscription.plan.monthly_request_limit,
        }, status=status.HTTP_200_OK)


class SubscriptionCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        organization = Organization.objects.filter(memberships__user=request.user).first()
        if organization is None:
            return Response({"detail": "No organization found."}, status=status.HTTP_404_NOT_FOUND)
        plan_code = request.data.get("plan_code", SubscriptionPlan.PLAN_FREE)
        subscription = ensure_subscription_for_organization(organization=organization, plan_code=plan_code, created_by=request.user)
        return Response({"plan_code": subscription.plan.code, "status": subscription.status}, status=status.HTTP_201_CREATED)
