import uuid

from django.conf import settings
from django.db import models


class APIEndpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="api_endpoints")
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10, default="GET")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "api_endpoints"
        unique_together = ("organization", "method", "path")


class UsageAggregationWindow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="usage_windows")
    window_start = models.DateTimeField()
    window_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "usage_aggregation_windows"
        unique_together = ("organization", "window_start", "window_end")


class UsageRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="usage_records")
    api_key = models.ForeignKey("api_keys.APIKey", on_delete=models.SET_NULL, null=True, blank=True, related_name="usage_records")
    endpoint = models.ForeignKey(APIEndpoint, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="usage_records")
    request_count = models.PositiveIntegerField(default=1)
    token_count = models.PositiveIntegerField(default=0)
    response_status = models.PositiveIntegerField(default=200)
    is_billable = models.BooleanField(default=True)
    captured_at = models.DateTimeField(auto_now_add=True)
    aggregation_window = models.ForeignKey(UsageAggregationWindow, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "usage_records"
        indexes = [models.Index(fields=["organization", "captured_at"])]
