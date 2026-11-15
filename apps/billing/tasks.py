from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.tenants.models import Organization

from .models import Invoice
from .services import build_invoice_for_organization


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def generate_monthly_invoices_task(self):
    now = timezone.now()
    start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = now

    created = []
    for organization in Organization.objects.all():
        if Invoice.objects.filter(
            organization=organization,
            billing_period_start=start,
            billing_period_end=end,
        ).exists():
            continue
        invoice = build_invoice_for_organization(
            organization=organization,
            billing_period_start=start,
            billing_period_end=end,
        )
        created.append(str(invoice.id))
    return {"created_invoices": created, "billing_period_start": start.isoformat(), "billing_period_end": end.isoformat()}
