from rest_framework import serializers

from .models import APIKey


class CreateAPIKeySerializer(serializers.Serializer):
    organization_id = serializers.UUIDField()
    name = serializers.CharField(max_length=120)
    permissions = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = [
            "id",
            "organization",
            "name",
            "key_prefix",
            "permissions",
            "is_active",
            "expires_at",
            "last_used_at",
            "revoked_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class RotateAPIKeySerializer(serializers.Serializer):
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
