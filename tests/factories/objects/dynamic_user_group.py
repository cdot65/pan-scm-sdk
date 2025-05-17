# tests/factories/objects/dynamic_user_group.py

"""Factory definitions for dynamic user group objects."""

import factory  # type: ignore
from faker import Faker

from scm.models.objects.dynamic_user_group import (
    DynamicUserGroupBaseModel,
    DynamicUserGroupUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# Dynamic User Group object factories
# ----------------------------------------------------------------------------


class DynamicUserGroupBaseFactory(factory.Factory):
    """Base factory for Dynamic User Group with common fields."""

    class Meta:
        """Meta class that defines the model for DynamicUserGroupBaseFactory."""

        model = DynamicUserGroupBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"dynamic_user_group_{n}")
    filter = "tag1 and tag2"
    description = fake.sentence()
    tag = ["test-tag", "environment-prod"]
    folder = None
    snippet = None
    device = None


# API Factory Classes - These return dictionaries for API testing


class DynamicUserGroupCreateApiFactory:
    """Factory for creating dynamic user group data for API tests."""

    @classmethod
    def with_folder(cls, name="test_group", folder="Texas", **kwargs):
        """Create a dynamic user group with folder."""
        data = {
            "name": name,
            "filter": "'tag.criticality.high'",
            "folder": folder,
            **kwargs,
        }
        return data

    @classmethod
    def with_snippet(cls, name="test_group", snippet="TestSnippet", **kwargs):
        """Create a dynamic user group with snippet."""
        data = {
            "name": name,
            "filter": "'tag.criticality.high'",
            "snippet": snippet,
            **kwargs,
        }
        return data

    @classmethod
    def with_device(cls, name="test_group", device="TestDevice", **kwargs):
        """Create a dynamic user group with device."""
        data = {
            "name": name,
            "filter": "'tag.criticality.high'",
            "device": device,
            **kwargs,
        }
        return data

    @classmethod
    def with_filter(cls, filter_expression="tag1 or tag2", **kwargs):
        """Create an instance with a specific filter expression."""
        return cls.with_folder(filter=filter_expression, **kwargs)

    @classmethod
    def with_complex_filter(cls, **kwargs):
        """Create an instance with a complex filter expression."""
        filter_expr = "(tag1 and tag2) or (tag3 and not tag4)"
        return cls.with_folder(filter=filter_expr, **kwargs)


class DynamicUserGroupUpdateApiFactory:
    """Factory for creating dynamic user group update data for API tests."""

    @classmethod
    def with_folder(
        cls,
        group_id="123e4567-e89b-12d3-a456-426655440000",
        name="updated_group",
        **kwargs,
    ):
        """Create update data for a dynamic user group."""
        # Create a Pydantic model instead of a dict
        data = {
            "id": group_id,
            "name": name,
            "filter": "'tag.criticality.medium'",
            **kwargs,
        }
        return DynamicUserGroupUpdateModel(**data)

    @classmethod
    def with_snippet(
        cls,
        group_id="123e4567-e89b-12d3-a456-426655440000",
        name="updated_group",
        snippet="TestSnippet",
        **kwargs,
    ):
        """Create a dynamic user group with snippet."""
        data = {
            "id": group_id,
            "name": name,
            "filter": "'tag.criticality.high'",
            "snippet": snippet,
            **kwargs,
        }
        return DynamicUserGroupUpdateModel(**data)

    @classmethod
    def with_device(
        cls,
        group_id="123e4567-e89b-12d3-a456-426655440000",
        name="updated_group",
        device="TestDevice",
        **kwargs,
    ):
        """Create a dynamic user group with device."""
        data = {
            "id": group_id,
            "name": name,
            "filter": "'tag.criticality.high'",
            "device": device,
            **kwargs,
        }
        return DynamicUserGroupUpdateModel(**data)

    @classmethod
    def with_filter(cls, filter_expression="tag1 or tag2", **kwargs):
        """Create an instance with a specific filter expression."""
        return cls.with_folder(filter=filter_expression, **kwargs)

    @classmethod
    def with_complex_filter(cls, **kwargs):
        """Create an instance with a complex filter expression."""
        filter_expr = "(tag1 and tag2) or (tag3 and not tag4)"
        return cls.with_folder(filter=filter_expr, **kwargs)

    @classmethod
    def minimal_update(cls, group_id=None, **kwargs):
        """Create an instance with minimal required fields for update."""
        if group_id is None:
            group_id = "123e4567-e89b-12d3-a456-426655440000"
        return cls.with_folder(
            group_id=group_id,
            name="MinimalUpdate",
            filter="minimal_tag1 or minimal_tag2",
            **kwargs,
        )


class DynamicUserGroupResponseFactory:
    """Factory for creating dynamic user group response data."""

    @classmethod
    def with_folder(
        cls,
        group_id="123e4567-e89b-12d3-a456-426655440000",
        name="test_group",
        folder="Texas",
        **kwargs,
    ):
        """Create a response dict with folder container."""
        data = {
            "id": group_id,
            "name": name,
            "filter": "'tag.criticality.high'",
            "folder": folder,
            **kwargs,
        }
        return data

    @classmethod
    def with_snippet(
        cls,
        group_id="123e4567-e89b-12d3-a456-426655440000",
        name="test_group",
        snippet="TestSnippet",
        **kwargs,
    ):
        """Create a response dict with snippet container."""
        data = {
            "id": group_id,
            "name": name,
            "filter": "'tag.criticality.high'",
            "snippet": snippet,
            **kwargs,
        }
        return data

    @classmethod
    def with_device(
        cls,
        group_id="123e4567-e89b-12d3-a456-426655440000",
        name="test_group",
        device="TestDevice",
        **kwargs,
    ):
        """Create a response dict with device container."""
        data = {
            "id": group_id,
            "name": name,
            "filter": "'tag.criticality.high'",
            "device": device,
            **kwargs,
        }
        return data

    @classmethod
    def from_request(cls, request_data):
        """Create a response dict based on a request data."""
        # Create a new dict to avoid modifying the original
        if hasattr(request_data, "model_dump"):
            data = request_data.model_dump()
        else:
            data = request_data.copy()

        if "id" not in data:
            data["id"] = "123e4567-e89b-12d3-a456-426655440000"
        return data


# ----------------------------------------------------------------------------
# Dynamic User Group model factories for Pydantic validation testing
# ----------------------------------------------------------------------------


class DynamicUserGroupCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for DynamicUserGroupCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for DynamicUserGroupCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"dynamic_user_group_{n}")
    filter = "tag1 and tag2"
    description = fake.sentence()
    tag = ["test-tag", "environment-prod"]
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict with all expected attributes."""
        return cls(**kwargs)

    @classmethod
    def build_with_invalid_name(cls, **kwargs):
        """Return a data dict with invalid name pattern."""
        return cls(name="invalid@name", **kwargs)

    @classmethod
    def build_with_empty_filter(cls, **kwargs):
        """Return a data dict with empty filter."""
        return cls(filter="", **kwargs)

    @classmethod
    def build_with_invalid_folder(cls, **kwargs):
        """Return a data dict with invalid folder pattern."""
        return cls(folder="Invalid@Folder", **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Return a data dict without any container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_duplicate_tags(cls, **kwargs):
        """Return a data dict with duplicate tags."""
        return cls(tag=["duplicate", "duplicate"], **kwargs)


class DynamicUserGroupUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for DynamicUserGroupUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for DynamicUserGroupUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = "test-dynamic-user-group"
    filter = "tag1 and tag2"
    description = fake.sentence()
    tag = ["test-tag", "environment-prod"]
    folder = "Texas"

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict for updating a dynamic user group."""
        return cls(**kwargs)

    @classmethod
    def build_with_invalid_fields(cls, **kwargs):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="not-a-uuid",
            name="invalid@name",
            filter="",
            **kwargs,
        )

    @classmethod
    def build_minimal_update(cls, **kwargs):
        """Return a data dict with minimal fields required for update."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="MinimalUpdate",
            filter="minimal_tag",
            description=None,
            tag=None,
            **kwargs,
        )

    @classmethod
    def build_with_duplicate_tags(cls, **kwargs):
        """Return a data dict with duplicate tags."""
        return cls(tag=["duplicate", "duplicate"], **kwargs)
