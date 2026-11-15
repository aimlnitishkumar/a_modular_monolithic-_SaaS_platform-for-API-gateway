from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import Organization

from .models import Invoice
from .services import build_invoice_for_organization


class InvoiceListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organization = Organization.objects.filter(memberships__user=request.user).first()
        if organization is None:
            return Response({"detail": "No organization found."}, status=status.HTTP_404_NOT_FOUND)
        invoices = Invoice.objects.filter(organization=organization).order_by("-created_at")
        return Response([
            {
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "total_amount": str(invoice.total_amount),
                "currency": invoice.currency,
                "status": invoice.status,
            }
            for invoice in invoices
        ], status=status.HTTP_200_OK)


class InvoiceGenerateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        organization = Organization.objects.filter(memberships__user=request.user).first()
        if organization is None:
            return Response({"detail": "No organization found."}, status=status.HTTP_404_NOT_FOUND)
        start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = timezone.now()
        invoice = build_invoice_for_organization(organization=organization, billing_period_start=start, billing_period_end=end)
        return Response({"invoice_number": invoice.invoice_number, "total_amount": str(invoice.total_amount)}, status=status.HTTP_201_CREATED)
