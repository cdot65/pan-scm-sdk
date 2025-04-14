# tests/scm/models/objects/test_application_group_models.py

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.objects import (
    ApplicationGroupCreateModel,
    ApplicationGroupResponseModel,
    ApplicationGroupUpdateModel,
)
from tests.factories.objects.application_group import (
    ApplicationGroupCreateModelFactory,
    ApplicationGroupResponseFactory,
    ApplicationGroupUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestApplicationGroupCreateModel:
    """Tests for ApplicationGroupCreateModel validation."""

    def test_application_group_create_model_valid(self):
        """Test validation with valid data."""
        data = ApplicationGroupCreateModelFactory.build_valid()
        model = ApplicationGroupCreateModel(**data)
        assert model.name == "TestApplicationGroup"
        assert model.folder == "Texas"
        assert model.members == ["app1", "app2"]

    def test_application_group_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = ApplicationGroupCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_application_group_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = ApplicationGroupCreateModelFactory.build_with_no_container()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_application_group_create_model_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "2 validation errors for ApplicationGroupCreateModel" in error_msg
        assert "name\n  Field required" in error_msg
        assert "members\n  Field required" in error_msg

    def test_application_group_create_model_invalid_name(self):
        """Test validation of name field constraints."""
        data = ApplicationGroupCreateModelFactory.build_with_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert "String should match pattern" in str(exc_info.value)

    def test_application_group_create_model_empty_members(self):
        """Test validation when members list is empty."""
        data = ApplicationGroupCreateModelFactory.build_with_empty_members()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert "List should have at least 1 item after validation" in str(exc_info.value)


class TestApplicationGroupUpdateModel:
    """Tests for ApplicationGroupUpdateModel validation."""

    def test_application_group_update_model_valid(self):
        """Test validation with valid update data."""
        data = ApplicationGroupUpdateModelFactory.build_valid()
        model = ApplicationGroupUpdateModel(**data)
        assert model.name == "UpdatedGroup"
        assert model.members == ["updated-app1", "updated-app2"]
        assert model.folder == "UpdatedFolder"

    def test_application_group_update_model_partial_update(self):
        """Test validation with partial update data."""
        data = ApplicationGroupUpdateModelFactory.build_minimal_update()
        model = ApplicationGroupUpdateModel(**data)
        assert model.name == "MinimalUpdate"
        assert model.id is not None
        assert model.folder is None

    def test_application_group_update_model_invalid_name(self):
        """Test validation of name field in update."""
        data = ApplicationGroupUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "String should match pattern" in error_msg or "Invalid UUID format" in error_msg

    def test_application_group_update_model_invalid_members(self):
        """Test validation of members field in update."""
        data = ApplicationGroupUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupUpdateModel(**data)
        assert "List should have at least 1 item after validation" in str(exc_info.value)


class TestApplicationGroupResponseModel:
    """Tests for ApplicationGroupResponseModel validation."""

    def test_application_group_response_model_valid(self):
        """Test validation with valid response data."""
        response_model = ApplicationGroupResponseFactory.with_folder()
        assert response_model.id is not None
        assert response_model.name is not None
        assert len(response_model.members) > 0
        assert response_model.folder == "Texas"
        assert response_model.snippet is None

    def test_application_group_response_model_missing_id(self):
        """Test validation when id field is missing."""
        data = {
            "name": "Microsoft 365 Access",
            "members": ["office365-consumer-access"],
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupResponseModel(**data)
        assert "Field required" in str(exc_info.value)

    def test_application_group_response_model_invalid_id(self):
        """Test validation of id field in response."""
        data = {
            "id": "invalid-uuid",
            "name": "Microsoft 365 Access",
            "members": ["office365-consumer-access"],
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_application_group_response_model_container_fields(self):
        """Test validation of container fields in response."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "Microsoft 365 Access",
            "members": ["office365-consumer-access"],
            "folder": "Invalid@Folder#",
        }
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupResponseModel(**data)
        assert "String should match pattern" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
