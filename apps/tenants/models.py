import uuid

from django.conf import settings
from django.db import models


class Organization(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_SUSPENDED = "suspended"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_SUSPENDED, "Suspended"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=120, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_organizations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organizations"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class Membership(models.Model):
    ROLE_PLATFORM_ADMIN = "platform_admin"
    ROLE_ORGANIZATION_OWNER = "organization_owner"
    ROLE_ORGANIZATION_ADMIN = "organization_admin"
    ROLE_DEVELOPER = "developer"
    ROLE_BILLING_MANAGER = "billing_manager"
    ROLE_READ_ONLY_ANALYST = "read_only_analyst"

    ROLE_CHOICES = [
        (ROLE_PLATFORM_ADMIN, "Platform Administrator"),
        (ROLE_ORGANIZATION_OWNER, "Organization Owner"),
        (ROLE_ORGANIZATION_ADMIN, "Organization Admin"),
        (ROLE_DEVELOPER, "Developer"),
        (ROLE_BILLING_MANAGER, "Billing Manager"),
        (ROLE_READ_ONLY_ANALYST, "Read-only Analyst"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=ROLE_DEVELOPER)
    is_owner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "user")
        db_table = "organization_memberships"

    def __str__(self) -> str:
        return f"{self.user.email} -> {self.organization.name} ({self.role})"
