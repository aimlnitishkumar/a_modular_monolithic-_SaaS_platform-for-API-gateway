from django.utils.text import slugify

from .models import Membership, Organization


def create_organization_for_user(*, user, name: str, slug: str | None = None) -> Organization:
    normalized_slug = slug or slugify(name)
    organization = Organization.objects.create(
        name=name,
        slug=normalized_slug,
        created_by=user,
    )
    Membership.objects.create(
        organization=organization,
        user=user,
        role=Membership.ROLE_ORGANIZATION_OWNER,
        is_owner=True,
    )
    return organization
