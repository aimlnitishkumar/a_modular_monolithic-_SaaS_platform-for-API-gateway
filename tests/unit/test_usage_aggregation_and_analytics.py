import json

import pytest
from django.contrib.auth import get_user_model

from apps.analytics.services import get_analytics_overview
from apps.tenants.services import create_organization_for_user
from apps.usage.models import APIEndpoint, UsageAggregationWindow, UsageRecord
from apps.usage.services import _IN_MEMORY_COUNTERS, aggregate_usage_snapshot

User = get_user_model()


@pytest.mark.django_db
def test_usage_snapshot_aggregates_redis_counters_into_usage_window():
    user = User.objects.create_user(email="usage@example.com", username="usage-user", password="StrongPass123!")
    org = create_organization_for_user(user=user, name="Usage Org", slug="usage-org")
    bucket_key = f"meterflow:usage:{org.id}:12345:GET:/api/v1/usage"
    _IN_MEMORY_COUNTERS[bucket_key] = json.dumps(
        {
            "organization_id": str(org.id),
            "api_key_id": None,
            "endpoint_path": "/api/v1/usage",
            "method": "GET",
            "request_count": 12,
            "token_count": 250,
            "window_start": "2024-01-01T00:00:00+00:00",
            "window_end": "2024-01-01T00:05:00+00:00",
        }
    )

    result = aggregate_usage_snapshot()
    matching_entry = next(item for item in result if item["organization_id"] == str(org.id))

    assert matching_entry["organization_id"] == str(org.id)
    assert UsageAggregationWindow.objects.filter(organization=org).count() == 1
    usage_record = UsageRecord.objects.get(organization=org)
    assert usage_record.request_count == 12
    assert usage_record.token_count == 250
    assert usage_record.aggregation_window is not None


@pytest.mark.django_db
def test_analytics_overview_reports_endpoint_breakdown():
    user = User.objects.create_user(email="analytics@example.com", username="analytics-user", password="StrongPass123!")
    org = create_organization_for_user(user=user, name="Analytics Org", slug="analytics-org")
    endpoint = APIEndpoint.objects.create(organization=org, path="/api/v1/metrics", method="GET")

    UsageRecord.objects.create(organization=org, endpoint=endpoint, request_count=20, token_count=150, is_billable=True)
    UsageRecord.objects.create(organization=org, endpoint=endpoint, request_count=10, token_count=50, is_billable=False)

    overview = get_analytics_overview(org.id)

    assert overview["total_requests"] == 30
    assert overview["billable_requests"] == 20
    assert overview["usage_by_endpoint"][0]["path"] == "/api/v1/metrics"
    assert overview["active_endpoints"] >= 1
