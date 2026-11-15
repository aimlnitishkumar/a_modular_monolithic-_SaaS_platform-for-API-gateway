import uuid

from django.db import models


class PricingRule(models.Model):
    METRIC_REQUESTS = "requests"
    METRIC_TOKENS = "tokens"
    METRIC_TRANSFER = "transfer"
    METRIC_COMPUTE = "compute"
    METRIC_STORAGE = "storage"
    METRIC_CHOICES = [
        (METRIC_REQUESTS, "Requests"),
        (METRIC_TOKENS, "Tokens"),
        (METRIC_TRANSFER, "Transfer"),
        (METRIC_COMPUTE, "Compute"),
        (METRIC_STORAGE, "Storage"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey("subscriptions.SubscriptionPlan", on_delete=models.CASCADE, related_name="pricing_rules")
    metric = models.CharField(max_length=20, choices=METRIC_CHOICES, default=METRIC_REQUESTS)
    unit_price = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    free_quota = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    applies_to = models.CharField(max_length=80, default="all")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pricing_rules"

    def __str__(self) -> str:
        return f"{self.plan.name} - {self.metric}"
