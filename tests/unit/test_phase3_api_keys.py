import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.api_keys.models import APIKey
from apps.api_keys.services import create_api_key_for_organization, verify_api_key
from apps.tenants.services import create_organization_for_user

User = get_user_model()


@pytest.mark.django_db
def test_create_api_key_returns_secret_once():
    user = User.objects.create_user(email="owner@example.com", username="owner", password="StrongPass123!")
    organization = create_organization_for_user(user=user, name="Acme", slug="acme")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/v1/keys/",
        {"organization_id": str(organization.id), "name": "Production key", "permissions": ["read", "write"]},
        format="json",
    )

    assert response.status_code == 201
    assert "secret" in response.data
    assert response.data["secret"].startswith("mf_")
    assert APIKey.objects.filter(name="Production key", organization=organization).exists()


@pytest.mark.django_db
def test_verify_api_key_rejects_wrong_secret_and_accepts_correct_one():
    user = User.objects.create_user(email="verify@example.com", username="verify-user", password="StrongPass123!")
    organization = create_organization_for_user(user=user, name="Verify Co", slug="verify-co")
    api_key, secret = create_api_key_for_organization(
        user=user,
        organization_id=str(organization.id),
        name="Validation key",
        permissions=["read"],
    )

    assert verify_api_key(secret) is not None
    assert verify_api_key(secret + "-wrong") is None
    assert APIKey.objects.filter(id=api_key.id, is_active=True).exists()


@pytest.mark.django_db
def test_revoke_api_key_marks_key_inactive():
    user = User.objects.create_user(email="revoke@example.com", username="revoke-user", password="StrongPass123!")
    organization = create_organization_for_user(user=user, name="Revoke Co", slug="revoke-co")
    api_key, _ = create_api_key_for_organization(
        user=user,
        organization_id=str(organization.id),
        name="Revoke me",
        permissions=["read"],
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.delete(f"/api/v1/keys/{api_key.id}/")

    assert response.status_code == 200
    api_key.refresh_from_db()
    assert api_key.is_active is False
    assert api_key.revoked_at is not None


@pytest.mark.django_db
def test_rotate_api_key_returns_new_secret_and_replaces_old():
    user = User.objects.create_user(email="rotate@example.com", username="rotate-user", password="StrongPass123!")
    organization = create_organization_for_user(user=user, name="Rotate Co", slug="rotate-co")
    api_key, _ = create_api_key_for_organization(
        user=user,
        organization_id=str(organization.id),
        name="Rotate me",
        permissions=["read"],
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(f"/api/v1/keys/{api_key.id}/rotate/", {}, format="json")

    assert response.status_code == 201
    assert "secret" in response.data
    assert response.data["secret"].startswith("mf_")

    api_key.refresh_from_db()
    assert api_key.is_active is False
    assert APIKey.objects.filter(rotated_from=api_key).exists()
