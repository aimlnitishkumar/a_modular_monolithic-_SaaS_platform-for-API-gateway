from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.gateway.services import resolve_api_key_from_request, validate_upstream_url
from apps.usage.services import record_usage, reserve_request_quota


@api_view(["POST"])
def gateway_request(request):
    api_key = resolve_api_key_from_request(request)
    if api_key is None:
        return Response({"detail": "Invalid or missing API key."}, status=status.HTTP_401_UNAUTHORIZED)

    organization = api_key.organization
    if organization is None:
        return Response({"detail": "API key is not associated with an organization."}, status=status.HTTP_400_BAD_REQUEST)

    payload = request.data or {}
    upstream_url = payload.get("upstream_url") or payload.get("url")
    if not validate_upstream_url(upstream_url):
        return Response({"detail": "Upstream URL is not allowed."}, status=status.HTTP_400_BAD_REQUEST)

    if not reserve_request_quota(str(organization.id), api_key.key_prefix):
        return Response({"detail": "Rate limit exceeded."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    response_payload = {
        "status": "accepted",
        "organization_id": str(organization.id),
        "key_prefix": api_key.key_prefix,
        "upstream_url": upstream_url,
        "method": request.method,
        "request_id": payload.get("request_id") or "req-local",
        "message": "Request routed through MeterFlow gateway.",
    }

    record_usage(
        organization_id=str(organization.id),
        api_key_id=str(api_key.id),
        endpoint_path=(payload.get("path") or "/gateway/request"),
        method=request.method,
        request_count=1,
        status_code=200,
        token_count=int(payload.get("token_count", 0) or 0),
    )

    return Response(response_payload, status=status.HTTP_200_OK)
