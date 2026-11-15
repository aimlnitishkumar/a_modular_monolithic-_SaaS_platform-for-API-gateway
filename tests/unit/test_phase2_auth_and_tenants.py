import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_register_user_success():
    client = APIClient()
    payload = {
        "email": "new.user@example.com",
        "username": "new-user",
        "first_name": "New",
        "last_name": "User",
        "password": "StrongPass123!",
    }

    response = client.post("/api/v1/auth/register/", payload, format="json")

    assert response.status_code == 201
    assert response.data["email"] == "new.user@example.com"
    assert User.objects.filter(email="new.user@example.com").exists()


@pytest.mark.django_db
def test_login_user_success():
    user = User.objects.create_user(
        email="login.user@example.com",
        username="login-user",
        password="StrongPass123!",
    )

    client = APIClient()
    response = client.post(
        "/api/v1/auth/login/",
        {"email": "login.user@example.com", "password": "StrongPass123!"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["email"] == user.email


@pytest.mark.django_db
def test_create_organization_requires_auth():
    client = APIClient()
    response = client.post("/api/v1/organizations/", {"name": "Acme", "slug": "acme"}, format="json")

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_create_organization_for_authenticated_user():
    user = User.objects.create_user(
        email="org.owner@example.com",
        username="org-owner",
        password="StrongPass123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/v1/organizations/", {"name": "Acme Corp", "slug": "acme-corp"}, format="json")

    assert response.status_code == 201
    assert response.data["name"] == "Acme Corp"
    assert response.data["slug"] == "acme-corp"
