# tests/scm/models/objects/test_dynamic_user_group_models.py

# External libraries
from uuid import UUID

from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.objects.dynamic_user_group import (
    DynamicUserGroupCreateModel,
    DynamicUserGroupResponseModel,
    DynamicUserGroupUpdateModel,
)
from tests.test_factories.objects.dynamic_user_group import (
    DynamicUserGroupCreateModelFactory,
    DynamicUserGroupUpdateModelFactory,
)


class TestDynamicUserGroupCreateModel:
    """Tests for DynamicUserGroupCreateModel validation."""

    def test_valid_dynamic_user_group_create(self):
        """Test that a valid DynamicUserGroupCreateModel can be created."""
        data = DynamicUserGroupCreateModelFactory.build_valid()

        model = DynamicUserGroupCreateModel(**data)
        assert model.name == data["name"]
        assert model.filter == data["filter"]
        assert model.description == data["description"]
        assert model.folder == data["folder"]
        assert model.tag == data["tag"]

    def test_name_required(self):
        """Test that name is required."""
        data = DynamicUserGroupCreateModelFactory.build_valid()
        del data["name"]

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupCreateModel(**data)
        assert "name" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_filter_required(self):
        """Test that filter is required."""
        data = DynamicUserGroupCreateModelFactory.build_valid()
        del data["filter"]

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupCreateModel(**data)
        assert "filter" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_container_required(self):
        """Test that exactly one container type is required."""
        data = DynamicUserGroupCreateModelFactory.build_with_no_container()

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_multiple_containers_not_allowed(self):
        """Test that multiple container types are not allowed."""
        data = DynamicUserGroupCreateModelFactory.build_with_multiple_containers()

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_tag_accepts_string(self):
        """Test that the tag field accepts a single string."""
        data = DynamicUserGroupCreateModelFactory.build_valid()
        data["tag"] = "single-tag"

        model = DynamicUserGroupCreateModel(**data)
        assert model.tag == ["single-tag"]

    def test_tag_accepts_list(self):
        """Test that the tag field accepts a list of strings."""
        data = DynamicUserGroupCreateModelFactory.build_valid()
        data["tag"] = ["tag1", "tag2"]

        model = DynamicUserGroupCreateModel(**data)
        assert model.tag == ["tag1", "tag2"]

    def test_tag_rejects_invalid_type(self):
        """Test that the tag field rejects invalid types."""
        data = DynamicUserGroupCreateModelFactory.build_valid()
        data["tag"] = {"invalid": "type"}

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupCreateModel(**data)
        assert "Tag must be a string or a list of strings" in str(exc_info.value)

    def test_tag_rejects_duplicate_items(self):
        """Test that the tag field rejects duplicate items."""
        data = DynamicUserGroupCreateModelFactory.build_with_duplicate_tags()

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupCreateModel(**data)
        assert "List items must be unique" in str(exc_info.value)

    def test_name_pattern_validation(self):
        """Test that name pattern is validated."""
        data = DynamicUserGroupCreateModelFactory.build_with_invalid_name()

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupCreateModel(**data)
        assert "String should match pattern" in str(exc_info.value)


class TestDynamicUserGroupUpdateModel:
    """Tests for DynamicUserGroupUpdateModel validation."""

    def test_valid_dynamic_user_group_update(self):
        """Test that a valid DynamicUserGroupUpdateModel can be created."""
        data = DynamicUserGroupUpdateModelFactory.build_valid()

        model = DynamicUserGroupUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.filter == data["filter"]
        assert model.description == data["description"]
        assert model.folder == data["folder"]
        assert model.tag == data["tag"]

    def test_id_optional(self):
        """Test that id is optional for update model."""
        data = DynamicUserGroupUpdateModelFactory.build_valid()
        del data["id"]

        model = DynamicUserGroupUpdateModel(**data)
        assert model.id is None

    def test_tag_accepts_string_update(self):
        """Test that the tag field accepts a single string in update model."""
        data = DynamicUserGroupUpdateModelFactory.build_valid()
        data["tag"] = "single-tag"

        model = DynamicUserGroupUpdateModel(**data)
        assert model.tag == ["single-tag"]

    def test_tag_accepts_list_update(self):
        """Test that the tag field accepts a list of strings in update model."""
        data = DynamicUserGroupUpdateModelFactory.build_valid()
        data["tag"] = ["tag1", "tag2"]

        model = DynamicUserGroupUpdateModel(**data)
        assert model.tag == ["tag1", "tag2"]

    def test_tag_rejects_invalid_type_update(self):
        """Test that the tag field rejects invalid types in update model."""
        data = DynamicUserGroupUpdateModelFactory.build_valid()
        data["tag"] = {"invalid": "type"}

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupUpdateModel(**data)
        assert "Tag must be a string or a list of strings" in str(exc_info.value)

    def test_tag_rejects_duplicate_items_update(self):
        """Test that the tag field rejects duplicate items in update model."""
        data = DynamicUserGroupUpdateModelFactory.build_with_duplicate_tags()

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupUpdateModel(**data)
        assert "List items must be unique" in str(exc_info.value)


class TestDynamicUserGroupResponseModel:
    """Tests for DynamicUserGroupResponseModel validation."""

    def test_valid_dynamic_user_group_response(self):
        """Test that a valid DynamicUserGroupResponseModel can be created."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-group",
            "filter": "'tag.User.Developer'",
            "description": "Test dynamic user group",
            "folder": "Shared",
            "tag": ["test-tag"],
        }

        model = DynamicUserGroupResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.filter == data["filter"]
        assert model.description == data["description"]
        assert model.folder == data["folder"]
        assert model.tag == data["tag"]

    def test_id_required_response(self):
        """Test that id is required for response model."""
        data = {
            "name": "test-group",
            "filter": "'tag.User.Developer'",
            "folder": "Shared",
        }

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupResponseModel(**data)
        assert "id" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_tag_accepts_string_response(self):
        """Test that the tag field accepts a single string in response model."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-group",
            "filter": "'tag.User.Developer'",
            "folder": "Shared",
            "tag": "single-tag",
        }

        model = DynamicUserGroupResponseModel(**data)
        assert model.tag == ["single-tag"]

    def test_tag_accepts_list_response(self):
        """Test that the tag field accepts a list of strings in response model."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-group",
            "filter": "'tag.User.Developer'",
            "folder": "Shared",
            "tag": ["tag1", "tag2"],
        }

        model = DynamicUserGroupResponseModel(**data)
        assert model.tag == ["tag1", "tag2"]

    def test_tag_rejects_invalid_type_response(self):
        """Test that the tag field rejects invalid types in response model."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-group",
            "filter": "'tag.User.Developer'",
            "folder": "Shared",
            "tag": {"invalid": "type"},
        }

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupResponseModel(**data)
        assert "Tag must be a string or a list of strings" in str(exc_info.value)

    def test_tag_rejects_duplicate_items_response(self):
        """Test that the tag field rejects duplicate items in response model."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-group",
            "filter": "'tag.User.Developer'",
            "folder": "Shared",
            "tag": ["tag1", "tag1"],
        }

        with pytest.raises(ValidationError) as exc_info:
            DynamicUserGroupResponseModel(**data)
        assert "List items must be unique" in str(exc_info.value)
