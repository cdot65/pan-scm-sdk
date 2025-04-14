# tests/scm/models/objects/test_tag_models.py

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects.tag import TagCreateModel, TagResponseModel, TagUpdateModel
from tests.test_factories.objects.tag import TagCreateModelFactory, TagUpdateModelFactory

# -------------------- Test Classes for Pydantic Models --------------------


class TestTagCreateModel:
    """Tests for TagCreateModel validation."""

    def test_tag_create_model_valid(self):
        """Test validation with valid data."""
        data = {
            "name": "test-tag",
            "folder": "Texas",
            "comments": "Test tag",
            "color": "Red",
        }
        model = TagCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.comments == data["comments"]
        assert model.color == data["color"]

    def test_tag_create_model_invalid_color(self):
        """Test validation with invalid color."""
        data = TagCreateModelFactory.build_with_invalid_color()
        with pytest.raises(ValidationError) as exc_info:
            TagCreateModel(**data)
        assert "Color must be one of" in str(exc_info.value)

    def test_tag_create_model_invalid_name(self):
        """Test validation with invalid name pattern."""
        data = {
            "name": "@invalid_name$",
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            TagCreateModel(**data)
        assert "String should match pattern" in str(exc_info.value)

    def test_tag_create_model_name_too_long(self):
        """Test validation when name exceeds maximum length."""
        data = {
            "name": "a" * 64,  # Max length is 63
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            TagCreateModel(**data)
        assert "String should have at most 63 characters" in str(exc_info.value)

    def test_tag_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = TagCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            TagCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_tag_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = {
            "name": "test-tag",
            "comments": "Test tag",
        }
        with pytest.raises(ValueError) as exc_info:
            TagCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_tag_create_model_comments_too_long(self):
        """Test validation when comments exceed maximum length."""
        data = {
            "name": "test-tag",
            "folder": "Texas",
            "comments": "a" * 1024,  # Max length is 1023
        }
        with pytest.raises(ValidationError) as exc_info:
            TagCreateModel(**data)
        assert "String should have at most 1023 characters" in str(exc_info.value)

    def test_tag_create_model_none_color(self):
        """Test validation when color is None."""
        data = {
            "name": "test-tag",
            "folder": "Texas",
            "color": None,
        }
        model = TagCreateModel(**data)
        assert model.color is None


class TestTagUpdateModel:
    """Tests for TagUpdateModel validation."""

    def test_tag_update_model_valid(self):
        """Test validation with valid update data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-tag",
            "comments": "Updated test tag",
            "color": "Blue",
        }
        model = TagUpdateModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.comments == data["comments"]
        assert model.color == data["color"]

    def test_tag_update_model_partial_update(self):
        """Test validation with partial update data."""
        data = {
            "name": "updated-tag",
            "comments": "Updated test tag",
        }
        model = TagUpdateModel(**data)
        assert model.name == data["name"]
        assert model.comments == data["comments"]
        assert model.color is None

    def test_tag_update_model_invalid_color(self):
        """Test validation with invalid color."""
        data = TagUpdateModelFactory.build_with_invalid_color()
        with pytest.raises(ValidationError) as exc_info:
            TagUpdateModel(**data)
        assert "Color must be one of" in str(exc_info.value)

    def test_tag_update_model_http_error_no_response_content(self):
        """Test validation with missing required fields."""
        data = {}
        with pytest.raises(ValidationError) as exc_info:
            TagUpdateModel(**data)
        assert "1 validation error for TagUpdateModel\nname\n  Field required" in str(
            exc_info.value
        )


class TestTagResponseModel:
    """Tests for TagResponseModel validation."""

    def test_tag_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-tag",
            "folder": "Texas",
            "comments": "Test tag",
            "color": "Red",
        }
        model = TagResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.comments == data["comments"]
        assert model.color == data["color"]

    def test_tag_response_model_optional_fields(self):
        """Test validation with optional fields in response."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-tag",
        }
        model = TagResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.comments is None
        assert model.color is None
        assert model.folder is None

    def test_tag_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "test-tag",
        }
        with pytest.raises(ValidationError) as exc_info:
            TagResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)
