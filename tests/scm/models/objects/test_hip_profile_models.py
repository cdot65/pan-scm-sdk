# tests/scm/models/objects/test_hip_profile_models.py

from uuid import UUID

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects import (
    HIPProfileCreateModel,
    HIPProfileUpdateModel,
    HIPProfileResponseModel,
)
from tests.factories import (
    HIPProfileCreateModelFactory,
    HIPProfileUpdateModelFactory,
)


# -------------------- Test Classes for Pydantic Models --------------------


class TestHIPProfileCreateModel:
    """Tests for HIPProfileCreateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            HIPProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "2 validation errors for HIPProfileCreateModel" in error_msg
        assert "name\n  Field required" in error_msg
        assert "match\n  Field required" in error_msg

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {"name": "test"}
        with pytest.raises(ValidationError) as exc_info:
            HIPProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for HIPProfileCreateModel" in error_msg
        assert "match\n  Field required" in error_msg

    def test_multiple_containers_error(self):
        """Test validation when multiple containers are provided."""
        data = HIPProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            HIPProfileCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_no_container_error(self):
        """Test validation when no container is provided."""
        data = HIPProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            HIPProfileCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_invalid_name_format(self):
        """Test validation for invalid name format."""
        data = HIPProfileCreateModelFactory.build_with_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            HIPProfileCreateModel(**data)
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_valid_model(self):
        """Test validation with valid data."""
        data = HIPProfileCreateModelFactory.build_valid()
        model = HIPProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.match == data["match"]
        assert model.folder == data["folder"]
        assert model.description == data["description"]


class TestHIPProfileUpdateModel:
    """Tests for HIPProfileUpdateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid": "data"}
        with pytest.raises(ValidationError) as exc_info:
            HIPProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "validation error" in error_msg
        assert "name\n  Field required" in error_msg
        assert "match\n  Field required" in error_msg
        assert "id\n  Field required" in error_msg

    def test_missing_id(self):
        """Test validation when 'id' field is missing."""
        data = HIPProfileCreateModelFactory.build_valid()
        with pytest.raises(ValidationError) as exc_info:
            HIPProfileUpdateModel(**data)
        assert "id\n  Field required" in str(exc_info.value)

    def test_invalid_id_format(self):
        """Test validation for invalid UUID format."""
        data = HIPProfileUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            HIPProfileUpdateModel(**data)
        assert "id\n  Input should be a valid UUID" in str(exc_info.value)

    def test_invalid_name_format(self):
        """Test validation for invalid name format."""
        data = HIPProfileUpdateModelFactory.build_with_invalid_fields()
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Valid UUID
        with pytest.raises(ValidationError) as exc_info:
            HIPProfileUpdateModel(**data)
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_missing_match(self):
        """Test validation when match field is missing."""
        data = HIPProfileUpdateModelFactory.build_with_invalid_fields()
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Valid UUID
        data["name"] = "ValidName"  # Valid name
        with pytest.raises(ValidationError) as exc_info:
            HIPProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "Input should be a valid string" in error_msg

    def test_minimal_update(self):
        """Test validation with minimal update data."""
        data = HIPProfileUpdateModelFactory.build_minimal_update()
        model = HIPProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.description == data["description"]

    def test_valid_model(self):
        """Test validation with valid data."""
        data = HIPProfileUpdateModelFactory.build_valid()
        model = HIPProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.match == data["match"]
        assert model.description == data["description"]


class TestHIPProfileResponseModel:
    """Tests for HIPProfileResponseModel validation."""

    def test_valid_model(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestHIPProfile",
            "match": "Any of the members of (hipobject1)",
            "folder": "Texas",
            "description": "Test HIP profile",
        }
        model = HIPProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.match == data["match"]
        assert model.folder == data["folder"]
        assert model.description == data["description"]

    def test_with_snippet(self):
        """Test validation with snippet container."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestHIPProfile",
            "match": "Any of the members of (hipobject1)",
            "snippet": "TestSnippet",
            "description": "Test HIP profile",
        }
        model = HIPProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.match == data["match"]
        assert model.snippet == data["snippet"]
        assert model.folder is None

    def test_with_device(self):
        """Test validation with device container."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestHIPProfile",
            "match": "Any of the members of (hipobject1)",
            "device": "TestDevice",
            "description": "Test HIP profile",
        }
        model = HIPProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.match == data["match"]
        assert model.device == data["device"]
        assert model.folder is None

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "description": "Test HIP profile",
        }
        with pytest.raises(ValidationError) as exc_info:
            HIPProfileResponseModel(**data)
        error_msg = str(exc_info.value)
        assert "2 validation errors for HIPProfileResponseModel" in error_msg
        assert "name\n  Field required" in error_msg
        assert "match\n  Field required" in error_msg
