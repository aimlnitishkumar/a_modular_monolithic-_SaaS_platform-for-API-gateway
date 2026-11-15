from decimal import Decimal

from django.utils import timezone

from apps.usage.models import UsageRecord

from .models import Invoice, InvoiceLineItem


def build_invoice_for_organization(*, organization, billing_period_start, billing_period_end, tax_rate=Decimal("0.10")) -> Invoice:
    records = UsageRecord.objects.filter(
        organization=organization,
        captured_at__gte=billing_period_start,
        captured_at__lt=billing_period_end,
        is_billable=True,
    )
    request_total = sum(r.request_count for r in records)
    token_total = sum(r.token_count for r in records)
    subtotal = Decimal(request_total) * Decimal("0.001") + Decimal(token_total) * Decimal("0.0001")
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    invoice_number = f"INV-{organization.slug.upper()}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    invoice = Invoice.objects.create(
        organization=organization,
        invoice_number=invoice_number,
        billing_period_start=billing_period_start,
        billing_period_end=billing_period_end,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total,
        status=Invoice.STATUS_ISSUED,
    )
    InvoiceLineItem.objects.create(
        invoice=invoice,
        description="API usage charges",
        quantity=Decimal(request_total),
        unit_price=Decimal("0.001"),
        amount=subtotal,
    )
    return invoice
