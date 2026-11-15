from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import redis
from django.conf import settings

from apps.tenants.models import Organization

from .models import APIEndpoint, UsageAggregationWindow, UsageRecord

_IN_MEMORY_COUNTERS: dict[str, str] = {}
_IN_MEMORY_LOCK = threading.Lock()


def _get_redis_client():
    try:
        client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()
        return client
    except Exception:
        return None


def _usage_window_start(bucket_window_seconds: int, bucket_id: int | None = None) -> tuple[datetime, datetime]:
    bucket_ts = bucket_id if bucket_id is not None else int(time.time() // bucket_window_seconds)
    start = datetime.fromtimestamp(bucket_ts * bucket_window_seconds, tz=timezone.utc)
    end = start + timedelta(seconds=bucket_window_seconds)
    return start, end


def increment_usage_counter(
    organization_id: str,
    *,
    api_key_id: str | None,
    endpoint_path: str,
    method: str,
    request_count: int = 1,
    token_count: int = 0,
    bucket_window_seconds: int = 300,
) -> str:
    bucket = int(time.time() // bucket_window_seconds)
    window_start, window_end = _usage_window_start(bucket_window_seconds, bucket)
    key = f"meterflow:usage:{organization_id}:{bucket}:{method}:{endpoint_path}"
    payload = {
        "organization_id": organization_id,
        "api_key_id": api_key_id,
        "endpoint_path": endpoint_path,
        "method": method,
        "request_count": request_count,
        "token_count": token_count,
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
    }
    if _get_redis_client() is not None:
        client = _get_redis_client()
        client.hincrby(key, "request_count", request_count)
        client.hincrby(key, "token_count", token_count)
        client.hset(
            key,
            mapping={
                "organization_id": organization_id,
                "api_key_id": api_key_id or "",
                "endpoint_path": endpoint_path,
                "method": method,
                "window_start": payload["window_start"],
                "window_end": payload["window_end"],
            },
        )
        client.expire(key, bucket_window_seconds)
        return key

    with _IN_MEMORY_LOCK:
        current = _IN_MEMORY_COUNTERS.get(key)
        if current is None:
            _IN_MEMORY_COUNTERS[key] = json.dumps(payload)
        else:
            data = json.loads(current)
            data["request_count"] += request_count
            data["token_count"] += token_count
            _IN_MEMORY_COUNTERS[key] = json.dumps(data)
    return key


def reserve_request_quota(organization_id: str, key_prefix: str, window_seconds: int = 60, limit: int = 100) -> bool:
    client = _get_redis_client()
    if client is not None:
        key = f"meterflow:rate:{organization_id}:{key_prefix}:{int(time.time() // window_seconds)}"
        try:
            with client.pipeline() as pipe:
                pipe.incr(key)
                pipe.expire(key, window_seconds)
                result = pipe.execute()
            return result[0] <= limit
        except Exception:
            pass

    now_bucket = int(time.time() // window_seconds)
    key = f"fallback:rate:{organization_id}:{key_prefix}:{now_bucket}"
    with _IN_MEMORY_LOCK:
        value = _IN_MEMORY_COUNTERS.get(key, "0")
        count = int(value) + 1 if value else 1
        _IN_MEMORY_COUNTERS[key] = str(count)
    return count <= limit


def record_usage(*, organization_id: str, api_key_id: str | None, endpoint_path: str, method: str, request_count: int = 1, status_code: int = 200, token_count: int = 0) -> UsageRecord:
    endpoint, _ = APIEndpoint.objects.get_or_create(
        organization_id=organization_id,
        method=method,
        path=endpoint_path,
    )
    usage = UsageRecord.objects.create(
        organization_id=organization_id,
        api_key_id=api_key_id,
        endpoint=endpoint,
        request_count=request_count,
        response_status=status_code,
        token_count=token_count,
        is_billable=status_code < 500,
    )
    increment_usage_counter(
        organization_id,
        api_key_id=api_key_id,
        endpoint_path=endpoint_path,
        method=method,
        request_count=request_count,
        token_count=token_count,
    )
    return usage


def _persist_usage_aggregate(payload: dict[str, Any]) -> dict[str, Any]:
    organization = Organization.objects.filter(pk=payload["organization_id"]).first()
    if organization is None:
        return payload

    window_start = datetime.fromisoformat(payload["window_start"]).astimezone(timezone.utc)
    window_end = datetime.fromisoformat(payload["window_end"]).astimezone(timezone.utc)
    window, _ = UsageAggregationWindow.objects.get_or_create(
        organization=organization,
        window_start=window_start,
        window_end=window_end,
    )

    endpoint, _ = APIEndpoint.objects.get_or_create(
        organization=organization,
        method=payload["method"],
        path=payload["endpoint_path"],
    )

    usage_record, created = UsageRecord.objects.get_or_create(
        organization=organization,
        endpoint=endpoint,
        api_key_id=payload["api_key_id"],
        aggregation_window=window,
        response_status=200,
        defaults={
            "request_count": payload["request_count"],
            "token_count": payload["token_count"],
            "is_billable": True,
        },
    )
    if not created:
        usage_record.request_count += payload["request_count"]
        usage_record.token_count += payload["token_count"]
        usage_record.is_billable = True
        usage_record.save(update_fields=["request_count", "token_count", "is_billable"])

    payload["aggregation_window_id"] = str(window.id)
    payload["usage_record_id"] = str(usage_record.id)
    return payload


def aggregate_usage_snapshot() -> list[dict[str, Any]]:
    client = _get_redis_client()
    processed: list[dict[str, Any]] = []

    if client is not None:
        for key in client.keys("meterflow:usage:*"):
            value = client.hgetall(key)
            if not value:
                continue
            payload = {
                "organization_id": value.get("organization_id"),
                "api_key_id": value.get("api_key_id") or None,
                "endpoint_path": value.get("endpoint_path", "/unknown"),
                "method": value.get("method", "GET"),
                "request_count": int(value.get("request_count", 0) or 0),
                "token_count": int(value.get("token_count", 0) or 0),
                "window_start": value.get("window_start"),
                "window_end": value.get("window_end"),
            }
            if not payload["organization_id"] or not payload["window_start"] or not payload["window_end"]:
                client.delete(key)
                continue
            if payload["request_count"] <= 0 and payload["token_count"] <= 0:
                client.delete(key)
                continue
            processed.append(_persist_usage_aggregate(payload))
            client.delete(key)
        return processed

    keys = list(_IN_MEMORY_COUNTERS)
    for key in keys:
        if not key.startswith("meterflow:usage:"):
            continue
        raw = _IN_MEMORY_COUNTERS.pop(key, None)
        if not raw:
            continue
        payload = json.loads(raw)
        if payload.get("request_count", 0) <= 0 and payload.get("token_count", 0) <= 0:
            continue
        processed.append(_persist_usage_aggregate(payload))
    return processed


def aggregate_usage_windows(organization_id: str | None = None) -> list[dict[str, Any]]:
    qs = UsageRecord.objects.filter(is_billable=True)
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    by_window = {}
    for item in qs:
        key = (item.captured_at.date().isoformat(), item.captured_at.hour)
        by_window.setdefault(key, {"request_count": 0, "token_count": 0})
        by_window[key]["request_count"] += item.request_count
        by_window[key]["token_count"] += item.token_count
    return [{"window": key[0], "hour": key[1], **value} for key, value in by_window.items()]
