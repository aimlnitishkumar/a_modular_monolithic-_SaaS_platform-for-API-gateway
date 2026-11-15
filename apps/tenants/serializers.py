from rest_framework import serializers

from .models import Membership, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "status", "created_at"]
        read_only_fields = ["id", "created_at"]


class CreateOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "slug"]

    def validate_slug(self, value):
        if not value:
            raise serializers.ValidationError("Slug is required.")
        return value


class MembershipSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ["id", "email", "role", "is_owner", "created_at"]
        read_only_fields = ["id", "email", "created_at"]

    def get_email(self, obj):
        return obj.user.email
