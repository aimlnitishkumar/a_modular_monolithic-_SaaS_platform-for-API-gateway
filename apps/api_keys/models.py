import uuid

from django.conf import settings
from django.db import models


class APIKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=120)
    key_prefix = models.CharField(max_length=32, unique=True, db_index=True)
    secret_hash = models.CharField(max_length=255)
    permissions = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    rotated_from = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replacements")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_keys"
        indexes = [models.Index(fields=["organization", "is_active", "expires_at"])]

    def __str__(self) -> str:
        return f"{self.key_prefix} - {self.name}"

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        from django.utils import timezone

        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired
