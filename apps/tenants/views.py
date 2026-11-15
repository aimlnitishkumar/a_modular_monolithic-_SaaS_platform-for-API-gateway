from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Organization
from .serializers import CreateOrganizationSerializer, OrganizationSerializer
from .services import create_organization_for_user


class OrganizationListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organizations = Organization.objects.filter(memberships__user=request.user).distinct()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CreateOrganizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization = create_organization_for_user(
            user=request.user,
            name=serializer.validated_data["name"],
            slug=serializer.validated_data.get("slug"),
        )
        return Response(OrganizationSerializer(organization).data, status=status.HTTP_201_CREATED)
