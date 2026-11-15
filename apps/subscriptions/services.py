from decimal import Decimal

from .models import Subscription, SubscriptionPlan


def ensure_subscription_for_organization(*, organization, plan_code: str = SubscriptionPlan.PLAN_FREE, created_by=None) -> Subscription:
    plan = SubscriptionPlan.objects.filter(code=plan_code).first()
    if plan is None:
        plan = SubscriptionPlan.objects.create(
            code=plan_code,
            name=plan_code.title(),
            monthly_request_limit=1000 if plan_code == SubscriptionPlan.PLAN_FREE else 100000,
            monthly_token_limit=0,
            base_price=Decimal("0.00") if plan_code == SubscriptionPlan.PLAN_FREE else Decimal("19.00"),
            currency="USD",
        )
    subscription, _ = Subscription.objects.get_or_create(
        organization=organization,
        defaults={"plan": plan, "status": Subscription.STATUS_ACTIVE, "created_by": created_by},
    )
    if subscription.plan != plan:
        subscription.plan = plan
        subscription.save(update_fields=["plan"])
    return subscription
