from decimal import Decimal

from .models import PricingRule


def calculate_pricing_for_usage(*, usage_count: int, token_count: int, plan_code: str) -> Decimal:
    total = Decimal("0.00")
    rules = PricingRule.objects.filter(plan__code=plan_code)
    for rule in rules:
        if rule.metric == PricingRule.METRIC_REQUESTS:
            billable = max(usage_count - int(rule.free_quota), 0)
            total += Decimal(billable) * rule.unit_price
        elif rule.metric == PricingRule.METRIC_TOKENS:
            billable = max(token_count - int(rule.free_quota), 0)
            total += Decimal(billable) * rule.unit_price
    return total
