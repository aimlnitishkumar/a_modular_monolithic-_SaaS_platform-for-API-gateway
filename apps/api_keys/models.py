from django.conf import settings
from django.db import models


class APIKey(models.Model):
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=120)
    key_prefix = models.CharField(max_length=32)
    secret_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_keys"
