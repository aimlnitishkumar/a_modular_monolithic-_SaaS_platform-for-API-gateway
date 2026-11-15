from django.db.models import Count, Sum

from apps.usage.models import APIEndpoint, UsageRecord


def get_analytics_overview(organization_id):
    qs = UsageRecord.objects.filter(organization_id=organization_id)
    total_requests = qs.aggregate(total=Sum("request_count"))["total"] or 0
    total_tokens = qs.aggregate(total=Sum("token_count"))["total"] or 0
    billable_requests = qs.filter(is_billable=True).aggregate(total=Sum("request_count"))["total"] or 0
    endpoint_breakdown = list(
        qs.values("endpoint__method", "endpoint__path")
        .annotate(request_count=Sum("request_count"), token_count=Sum("token_count"), hit_count=Count("id"))
        .order_by("-request_count")[:10]
    )
    return {
        "organization_id": str(organization_id),
        "total_requests": int(total_requests),
        "total_tokens": int(total_tokens),
        "billable_requests": int(billable_requests),
        "active_endpoints": APIEndpoint.objects.filter(organization_id=organization_id).count(),
        "usage_by_endpoint": [
            {
                "method": row["endpoint__method"],
                "path": row["endpoint__path"],
                "request_count": int(row["request_count"] or 0),
                "token_count": int(row["token_count"] or 0),
                "hit_count": int(row["hit_count"] or 0),
            }
            for row in endpoint_breakdown
        ],
    }
