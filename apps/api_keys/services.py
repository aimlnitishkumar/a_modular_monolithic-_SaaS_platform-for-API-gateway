import hashlib
import secrets
from typing import Any

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.crypto import constant_time_compare

from apps.tenants.models import Membership, Organization

from .models import APIKey


def _hash_secret(secret: str) -> str:
    salt = secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt.encode("utf-8"), 200_000)
    return f"{salt}${digest.hex()}"


def _verify_secret(secret: str, secret_hash: str) -> bool:
    if not secret or not secret_hash or "$" not in secret_hash:
        return False

    salt, _, digest_hex = secret_hash.partition("$")
    digest = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt.encode("utf-8"), 200_000)
    return constant_time_compare(digest.hex(), digest_hex)


def generate_api_key() -> tuple[str, str]:
    key_prefix = f"{settings.API_KEY_PREFIX}{secrets.token_hex(6)}"
    secret = f"{key_prefix}.{secrets.token_urlsafe(32)}"
    return key_prefix, secret


def create_api_key_for_organization(*, user: Any, organization_id: str, name: str, permissions: list[str] | None = None, expires_at: Any | None = None) -> tuple[APIKey, str]:
    organization = Organization.objects.select_related("created_by").get(id=organization_id)

    if not Membership.objects.filter(user=user, organization=organization).exists():
        raise PermissionDenied("You do not have access to this organization.")

    key_prefix, secret = generate_api_key()
    api_key = APIKey.objects.create(
        organization=organization,
        name=name,
        key_prefix=key_prefix,
        secret_hash=_hash_secret(secret),
        permissions=permissions or [],
        expires_at=expires_at,
        created_by=user,
    )
    return api_key, secret


def verify_api_key(secret: str | None) -> APIKey | None:
    if not secret or "." not in secret:
        return None

    key_prefix, _, _ = secret.partition(".")
    api_key = (
        APIKey.objects.filter(key_prefix=key_prefix, is_active=True)
        .select_related("organization", "created_by")
        .first()
    )

    if api_key is None or api_key.is_expired:
        return None

    if not _verify_secret(secret, api_key.secret_hash):
        return None

    api_key.last_used_at = timezone.now()
    api_key.save(update_fields=["last_used_at"])
    return api_key


def revoke_api_key(api_key: APIKey) -> APIKey:
    api_key.is_active = False
    api_key.revoked_at = timezone.now()
    api_key.save(update_fields=["is_active", "revoked_at", "updated_at"])
    return api_key


def rotate_api_key(*, user: Any, api_key: APIKey, expires_at: Any | None = None) -> tuple[APIKey, str]:
    if not api_key.is_active:
        raise PermissionDenied("Cannot rotate an inactive API key.")

    new_prefix, new_secret = generate_api_key()
    new_key = APIKey.objects.create(
        organization=api_key.organization,
        name=api_key.name,
        key_prefix=new_prefix,
        secret_hash=_hash_secret(new_secret),
        permissions=list(api_key.permissions),
        expires_at=expires_at or api_key.expires_at,
        created_by=user,
        rotated_from=api_key,
    )
    revoke_api_key(api_key)
    return new_key, new_secret
