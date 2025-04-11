# tests/scm/models/objects/test_application_group_models.py

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects import (
    ApplicationGroupCreateModel,
    ApplicationGroupResponseModel,
    ApplicationGroupUpdateModel,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestApplicationGroupCreateModel:
    """Tests for ApplicationGroupCreateModel validation."""

    def test_application_group_create_model_valid(self):
        """Test validation with valid data."""
        data = {
            "name": "Microsoft 365 Access",
            "folder": "Texas",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
        }
        model = ApplicationGroupCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.members == data["members"]

    def test_application_group_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "Microsoft 365 Access",
            "folder": "Texas",
            "snippet": "office365",
            "device": "firewall1",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
        }
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_application_group_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = {
            "name": "Microsoft 365 Access",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
        }
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
        data = {
            "name": "invalid@name#",
            "folder": "Texas",
            "members": ["app1", "app2"],
        }
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert "String should match pattern" in str(exc_info.value)

    def test_application_group_create_model_empty_members(self):
        """Test validation when members list is empty."""
        data = {
            "name": "test-group",
            "folder": "Texas",
            "members": [],
        }
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupCreateModel(**data)
        assert "List should have at least 1 item after validation" in str(exc_info.value)


class TestApplicationGroupUpdateModel:
    """Tests for ApplicationGroupUpdateModel validation."""

    def test_application_group_update_model_valid(self):
        """Test validation with valid update data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "Microsoft 365 Access",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
            "folder": "Texas",
        }
        model = ApplicationGroupUpdateModel(**data)
        assert model.name == data["name"]
        assert model.members == data["members"]
        assert model.folder == data["folder"]

    def test_application_group_update_model_partial_update(self):
        """Test validation with partial update data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "Microsoft 365 Access",
            "members": ["office365-consumer-access"],
        }
        model = ApplicationGroupUpdateModel(**data)
        assert model.name == data["name"]
        assert model.members == data["members"]
        assert model.folder is None

    def test_application_group_update_model_invalid_name(self):
        """Test validation of name field in update."""
        data = {
            "name": "invalid@name#",
            "members": ["app1"],
        }
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupUpdateModel(**data)
        assert "String should match pattern" in str(exc_info.value)

    def test_application_group_update_model_invalid_members(self):
        """Test validation of members field in update."""
        data = {
            "name": "test-group",
            "members": [],
        }
        with pytest.raises(ValidationError) as exc_info:
            ApplicationGroupUpdateModel(**data)
        assert "List should have at least 1 item after validation" in str(exc_info.value)


class TestApplicationGroupResponseModel:
    """Tests for ApplicationGroupResponseModel validation."""

    def test_application_group_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "Microsoft 365 Access",
            "members": ["office365-consumer-access", "office365-enterprise-access"],
            "folder": "Texas",
        }
        model = ApplicationGroupResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.members == data["members"]
        assert model.folder == data["folder"]

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
