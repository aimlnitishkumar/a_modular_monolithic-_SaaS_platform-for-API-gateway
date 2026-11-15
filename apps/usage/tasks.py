from __future__ import annotations

from celery import shared_task

from .services import aggregate_usage_snapshot


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def aggregate_usage_task(self):
    summary = aggregate_usage_snapshot()
    return {"processed_records": len(summary), "summary": summary}
