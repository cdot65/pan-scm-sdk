# tests/scm/models/objects/test_application.py

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects import (
    ApplicationCreateModel,
    ApplicationUpdateModel,
    ApplicationResponseModel,
)
from tests.factories import (
    ApplicationCreateModelFactory,
    ApplicationUpdateModelFactory,
    ApplicationResponseFactory,
)


# -------------------- Test Classes for Pydantic Models --------------------


class TestApplicationCreateModel:
    """Tests for ApplicationCreateModel validation."""

    def test_application_create_model_valid(self):
        """Test validation with valid data."""
        data = ApplicationCreateModelFactory.build_valid()
        model = ApplicationCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data.get("folder")
        assert model.category == data["category"]
        assert model.subcategory == data["subcategory"]
        assert model.technology == data["technology"]
        assert model.risk == data["risk"]
        assert model.description == data.get("description")
        assert model.ports == data.get("ports")
        assert model.transfers_files == data.get("transfers_files")
        assert model.has_known_vulnerabilities == data.get("has_known_vulnerabilities")

    def test_application_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = ApplicationCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateModel(**data)
        assert "Exactly one of 'folder' or 'snippet' must be provided." in str(
            exc_info.value
        )

    def test_application_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = ApplicationCreateModelFactory.build_with_no_container()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateModel(**data)
        assert "Exactly one of 'folder' or 'snippet' must be provided." in str(
            exc_info.value
        )

    def test_application_create_model_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = ApplicationCreateModelFactory.build_with_missing_required_fields()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "5 validation errors for ApplicationCreateModel" in error_msg

    def test_application_create_model_invalid_name(self):
        """Test validation of name field constraints."""
        data = ApplicationCreateModelFactory.build_valid(name="invalid@name#")
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateModel(**data)
        assert (
            "1 validation error for ApplicationCreateModel\nname\n  String should match pattern '^[a-zA-Z0-9_ \\.-]+$'"
            in str(exc_info.value)
        )

    def test_application_create_model_invalid_risk(self):
        """Test validation of risk field."""
        data = ApplicationCreateModelFactory.build_valid(risk="invalid")
        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateModel(**data)
        assert (
            "1 validation error for ApplicationCreateModel\nrisk\n  Input should be a valid integer, unable to parse string as an integer"
            in str(exc_info.value)
        )

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
        data = ApplicationUpdateModelFactory.build_valid(
            name="internal-chat",
            category="collaboration",
            subcategory="instant-messaging",
            technology="client-server",
            risk=2,
            description="Updated description",
        )
        model = ApplicationUpdateModel(**data)
        assert model.name == data["name"]
        assert model.category == data["category"]
        assert model.description == data["description"]

    def test_application_update_model_partial_update(self):
        """Test validation with partial update data."""
        data = ApplicationUpdateModelFactory.build_partial_update(
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
            subcategory="instant-messaging",
            technology="client-server",
            risk=2,
            description="Updated description",
        )
        with pytest.raises(ValidationError) as exc_info:
            ApplicationUpdateModel(**data)
        assert (
            "1 validation error for ApplicationUpdateModel\nname\n  String should match pattern '^[a-zA-Z0-9_ \\.-]+$'"
            in str(exc_info.value)
        )

    def test_application_update_model_invalid_risk(self):
        """Test validation of risk field in update."""
        data = ApplicationUpdateModelFactory.build_valid(
            name="internal-chat",
            category="collaboration",
            subcategory="instant-messaging",
            technology="client-server",
            risk="invalid",
        )
        with pytest.raises(ValidationError) as exc_info:
            ApplicationUpdateModel(**data)
        assert "1 validation error for ApplicationUpdateModel\nrisk" in str(
            exc_info.value
        )


class TestApplicationResponseModel:
    """Tests for ApplicationResponseModel validation."""

    def test_application_response_model_valid(self):
        """Test validation with valid response data."""
        data = ApplicationCreateModelFactory.build_valid()
        model = ApplicationResponseModel(**data)
        assert model.name == data["name"]
        assert model.category == data["category"]
        assert model.subcategory == data.get("subcategory")
        assert model.technology == data.get("technology")

    def test_application_response_model_optional_fields(self):
        """Test validation with optional fields in response."""
        data = (
            ApplicationResponseFactory.without_subcategory_and_technology().model_dump()
        )
        model = ApplicationResponseModel(**data)
        assert model.name == data["name"]
        assert model.subcategory is None
        assert model.technology is None

    def test_application_response_model_invalid_id(self):
        """Test validation of id field in response."""
        data = ApplicationCreateModelFactory.build_valid(id="invalid-uuid")
        with pytest.raises(ValidationError) as exc_info:
            ApplicationResponseModel(**data)
        assert (
            "1 validation error for ApplicationResponseModel\nid\n  Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1"
            in str(exc_info.value)
        )

    def test_application_response_model_description_length(self):
        """Test validation of extended description length in response."""
        data = ApplicationCreateModelFactory.build_valid(
            description="x" * 4000  # Test with a long description
        )
        model = ApplicationResponseModel(**data)
        assert model.description == data["description"]


# -------------------- End of Test Classes --------------------
