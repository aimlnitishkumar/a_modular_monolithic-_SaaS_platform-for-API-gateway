from __future__ import annotations

from urllib.parse import urlparse

from apps.api_keys.services import verify_api_key

ALLOWED_UPSTREAM_HOSTS = {"example.com", "api.example.com", "localhost"}


def validate_upstream_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.hostname or ""
    return host in ALLOWED_UPSTREAM_HOSTS


def resolve_api_key_from_request(request) -> object | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("ApiKey "):
        token = auth_header.split(" ", 1)[1].strip()
    else:
        token = request.headers.get("X-API-Key") or request.headers.get("X-API-Key-Id")
    if not token:
        return None
    return verify_api_key(token)
