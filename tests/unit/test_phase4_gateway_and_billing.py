import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.api_keys.services import create_api_key_for_organization
from apps.billing.models import Invoice
from apps.billing.services import build_invoice_for_organization
from apps.tenants.services import create_organization_for_user
from apps.usage.models import UsageRecord

User = get_user_model()


@pytest.mark.django_db
def test_gateway_request_accepts_valid_api_key():
    user = User.objects.create_user(email="gateway@example.com", username="gateway-user", password="StrongPass123!")
    org = create_organization_for_user(user=user, name="Gateway Org", slug="gateway-org")
    api_key, secret = create_api_key_for_organization(
        user=user,
        organization_id=str(org.id),
        name="Gateway Key",
        permissions=["read"],
    )

    client = APIClient()
    response = client.post(
        "/gateway/v1/request/",
        {"upstream_url": "https://example.com", "path": "/api/v1/ping", "request_id": "abc-123"},
        format="json",
        HTTP_AUTHORIZATION=f"ApiKey {secret}",
    )

    assert response.status_code == 200
    assert response.data["status"] == "accepted"
    assert response.data["organization_id"] == str(org.id)


@pytest.mark.django_db
def test_build_invoice_creates_positive_total():
    user = User.objects.create_user(email="billing@example.com", username="billing-user", password="StrongPass123!")
    org = create_organization_for_user(user=user, name="Billing Org", slug="billing-org")
    usage = UsageRecord.objects.create(
        organization=org,
        request_count=30,
        token_count=500,
        response_status=200,
        is_billable=True,
    )

    invoice = build_invoice_for_organization(
        organization=org,
        billing_period_start=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        billing_period_end=timezone.now().replace(hour=23, minute=59, second=59, microsecond=0),
    )

    assert invoice.status == Invoice.STATUS_ISSUED
    assert invoice.total_amount > 0
    assert UsageRecord.objects.filter(id=usage.id).exists()
