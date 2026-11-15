from typing import Any

from django.contrib.auth import authenticate

from .models import User


def register_user(*, email: str, password: str, username: str, first_name: str = "", last_name: str = "") -> User:
    return User.objects.create_user(
        email=email,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )


def authenticate_user(*, email: str, password: str, request: Any | None = None) -> User | None:
    return authenticate(request=request, email=email, password=password)
