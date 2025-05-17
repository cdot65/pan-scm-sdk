# tests/scm/models/objects/test_application_models.py

"""Tests for application models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.objects import (
    ApplicationCreateModel,
    ApplicationResponseModel,
    ApplicationUpdateModel,
)
from tests.factories.objects.application import (
    ApplicationCreateModelFactory,
    ApplicationResponseModelFactory,
    ApplicationUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestApplicationCreateModel:
    """Tests for ApplicationCreateModel validation."""

    def test_application_create_model_valid(self):
        """Test validation with valid data."""
        data = ApplicationCreateModelFactory.build_valid()
        model = ApplicationCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.category == data["category"]
        assert model.subcategory == data["subcategory"]
        assert model.technology == data["technology"]
        assert model.risk == data["risk"]
        assert model.description == data["description"]
        assert model.ports == data["ports"]

    def test_application_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = ApplicationCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateModel(**data)
        assert "Exactly one of 'folder' or 'snippet' must be provided." in str(exc_info.value)

    def test_application_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = ApplicationCreateModelFactory.build_with_no_containers()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateModel(**data)
        assert "Exactly one of 'folder' or 'snippet' must be provided." in str(exc_info.value)

    def test_application_create_model_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {
            "name": "internal-chat",
            "folder": "MainFolder",
        }
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "category\n  Field required" in error_msg
        assert "subcategory\n  Field required" in error_msg
        assert "technology\n  Field required" in error_msg
        assert "risk\n  Field required" in error_msg

    def test_application_create_model_invalid_name(self):
        """Test validation of name field constraints."""
        data = ApplicationCreateModelFactory.build_valid(name="invalid@name#")
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateModel(**data)
        assert "String should match pattern" in str(exc_info.value)

    def test_application_create_model_invalid_risk(self):
        """Test validation of risk field."""
        data = ApplicationCreateModelFactory.build_valid(risk="invalid")
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateModel(**data)
        assert "Input should be a valid integer" in str(exc_info.value)

    def test_application_create_model_boolean_fields(self):
        """Test validation of boolean fields."""
        data = ApplicationCreateModelFactory.build_valid(
            evasive=True,
            pervasive=True,
            excessive_bandwidth_use=True,
            used_by_malware=True,
            transfers_files=True,
            has_known_vulnerabilities=True,
            tunnels_other_apps=True,
            prone_to_misuse=True,
            no_certifications=True,
        )
        model = ApplicationCreateModel(**data)
        assert model.evasive is True
        assert model.pervasive is True
        assert model.excessive_bandwidth_use is True
        assert model.used_by_malware is True
        assert model.transfers_files is True
        assert model.has_known_vulnerabilities is True
        assert model.tunnels_other_apps is True
        assert model.prone_to_misuse is True
        assert model.no_certifications is True


class TestApplicationUpdateModel:
    """Tests for ApplicationUpdateModel validation."""

    def test_application_update_model_valid(self):
        """Test validation with valid update data."""
        data = ApplicationUpdateModelFactory.build_valid()
        model = ApplicationUpdateModel(**data)
        assert model.name == data["name"]
        assert model.category == data["category"]
        assert model.description == data["description"]

    def test_application_update_model_partial_update(self):
        """Test validation with partial update data."""
        data = ApplicationUpdateModelFactory.build_valid(
            name="internal-chat",
            description="Updated description",
            category="collaboration",
            subcategory="instant-messaging",
            technology="client-server",
            risk=2,
        )
        model = ApplicationUpdateModel(**data)
        assert model.name == data["name"]
        assert model.description == data["description"]

    def test_application_update_model_invalid_name(self):
        """Test validation of name field in update."""
        data = ApplicationUpdateModelFactory.build_valid(
            name="invalid@name#",
            category="collaboration",
        )
        with pytest.raises(ValidationError) as exc_info:
            ApplicationUpdateModel(**data)
        assert "String should match pattern" in str(exc_info.value)

    def test_application_update_model_invalid_risk(self):
        """Test validation of risk field in update."""
        data = ApplicationUpdateModelFactory.build_valid(
            name="internal-chat",
            risk="invalid",
        )
        with pytest.raises(ValidationError) as exc_info:
            ApplicationUpdateModel(**data)
        assert "Input should be a valid integer" in str(exc_info.value)


class TestApplicationResponseModel:
    """Tests for ApplicationResponseModel validation."""

    def test_application_response_model_valid(self):
        """Test validation of a complete response model."""
        data = ApplicationResponseModelFactory.build_valid()
        model = ApplicationResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.category == data["category"]
        assert model.subcategory == data["subcategory"]
        assert model.technology == data["technology"]
        assert model.risk == data["risk"]
        assert model.description == data["description"]

    def test_application_response_model_optional_fields(self):
        """Test validation with optional fields in response."""
        data = ApplicationResponseModelFactory.build_valid(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="internal-chat",
            category="collaboration",
            subcategory="instant-messaging",
            technology="client-server",
            risk=2,
        )
        model = ApplicationResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]

    def test_application_response_model_invalid_id(self):
        """Test validation of id field in response."""
        data = ApplicationResponseModelFactory.build_valid(
            id="invalid-uuid",
            name="internal-chat",
            category="collaboration",
            risk=2,
        )
        with pytest.raises(ValidationError) as exc_info:
            ApplicationResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_application_response_model_description_length(self):
        """Test validation of extended description length in response."""
        data = ApplicationResponseModelFactory.build_valid(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="internal-chat",
            category="collaboration",
            subcategory="instant-messaging",
            technology="client-server",
            risk=2,
            description="x" * 4096,  # Test with a long description
        )
        with pytest.raises(ValidationError) as exc_info:
            ApplicationResponseModel(**data)
        assert "String should have at most 4094 characters" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
