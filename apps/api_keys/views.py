from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import Organization

from .models import APIKey
from .serializers import APIKeySerializer, CreateAPIKeySerializer, RotateAPIKeySerializer
from .services import create_api_key_for_organization, revoke_api_key, rotate_api_key


class APIKeyListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organization_ids = request.user.memberships.values_list("organization_id", flat=True)
        keys = APIKey.objects.filter(organization_id__in=organization_ids).order_by("-created_at")
        serializer = APIKeySerializer(keys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CreateAPIKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = Organization.objects.filter(id=serializer.validated_data["organization_id"]).first()
        if organization is None:
            return Response({"detail": "Organization not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.memberships.filter(organization=organization).exists():
            raise PermissionDenied("You are not a member of this organization.")

        api_key, secret = create_api_key_for_organization(
            user=request.user,
            organization_id=str(organization.id),
            name=serializer.validated_data["name"],
            permissions=serializer.validated_data.get("permissions", []),
            expires_at=serializer.validated_data.get("expires_at"),
        )

        payload = APIKeySerializer(api_key).data
        payload["secret"] = secret
        return Response(payload, status=status.HTTP_201_CREATED)


class APIKeyDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        api_key = APIKey.objects.filter(id=kwargs["pk"]).first()
        if api_key is None:
            return Response({"detail": "API key not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.memberships.filter(organization=api_key.organization).exists():
            raise PermissionDenied("You are not allowed to manage this API key.")

        revoke_api_key(api_key)
        return Response({"status": "revoked", "id": str(api_key.id)}, status=status.HTTP_200_OK)


class APIKeyRotateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        api_key = APIKey.objects.filter(id=kwargs["pk"]).first()
        if api_key is None:
            return Response({"detail": "API key not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.memberships.filter(organization=api_key.organization).exists():
            raise PermissionDenied("You are not allowed to rotate this API key.")

        serializer = RotateAPIKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_key, new_secret = rotate_api_key(
            user=request.user,
            api_key=api_key,
            expires_at=serializer.validated_data.get("expires_at"),
        )

        payload = APIKeySerializer(new_key).data
        payload["secret"] = new_secret
        return Response(payload, status=status.HTTP_201_CREATED)
