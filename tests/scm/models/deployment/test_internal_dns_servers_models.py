"""Tests for internal DNS server pydantic models."""

from ipaddress import IPv4Address
import uuid

from pydantic import ValidationError
import pytest

from scm.models.deployment.internal_dns_servers import (
    InternalDnsServersBaseModel,
    InternalDnsServersCreateModel,
    InternalDnsServersResponseModel,
    InternalDnsServersUpdateModel,
)
from tests.test_factories.deployment.internal_dns_servers import (
    InternalDnsServersCreateModelFactory,
    InternalDnsServersResponseModelFactory,
    InternalDnsServersUpdateModelFactory,
)


class TestInternalDnsServersBaseModel:
    """Tests for the InternalDnsServersBaseModel."""

    def test_valid_base_model(self):
        """Test creating a valid base model."""
        model = InternalDnsServersBaseModel(
            name="test-dns-server",
            domain_name=["example.com", "test.com"],
            primary="192.168.1.1",
            secondary="8.8.8.8",
        )
        assert model.name == "test-dns-server"
        assert model.domain_name == ["example.com", "test.com"]
        assert model.primary == IPv4Address("192.168.1.1")
        assert model.secondary == IPv4Address("8.8.8.8")

    def test_ip_address_serialization(self):
        """Test IP address serialization to string."""
        model = InternalDnsServersBaseModel(
            name="test-dns-server",
            domain_name=["example.com"],
            primary="192.168.1.1",
            secondary="8.8.8.8",
        )

        serialized = model.model_dump(exclude_unset=True)
        # Verify primary and secondary are strings in serialized output
        assert isinstance(serialized["primary"], str)
        assert serialized["primary"] == "192.168.1.1"
        assert isinstance(serialized["secondary"], str)
        assert serialized["secondary"] == "8.8.8.8"

    def test_ip_address_serialization_none(self):
        """Test IP address serialization when secondary is None."""
        model = InternalDnsServersBaseModel(
            name="test-dns-server",
            domain_name=["example.com"],
            primary="192.168.1.1",
            secondary=None,
        )
        serialized = model.model_dump(exclude_unset=True)
        assert serialized["secondary"] is None

    def test_domain_name_validator_string(self):
        """Test domain_name validator converts string to list."""
        model = InternalDnsServersBaseModel(
            name="test-dns-server",
            domain_name="example.com",  # Single string
            primary="192.168.1.1",
        )
        assert model.domain_name == ["example.com"]

    def test_domain_name_validator_none(self):
        """Test domain_name validator converts None to empty list but then fails validation."""
        # First test the before validator directly
        result = InternalDnsServersBaseModel.validate_domain_name(None)
        assert result == []

        # Now test the full model validation with None
        with pytest.raises(ValidationError) as exc_info:
            InternalDnsServersBaseModel(
                name="test-dns-server",
                domain_name=None,
                primary="192.168.1.1",
            )
        assert "domain_name" in str(exc_info.value)

    def test_domain_name_empty_list(self):
        """Test validation fails with empty domain_name list."""
        with pytest.raises(ValidationError) as exc_info:
            InternalDnsServersBaseModel(
                name="test-dns-server",
                domain_name=[],
                primary="192.168.1.1",
            )
        assert "domain_name" in str(exc_info.value)
        assert "item" in str(exc_info.value)  # Check for 'at least 1 item' error

    def test_domain_name_validator_not_empty(self):
        """Test domain_name_not_empty validator directly."""
        # Test empty list case
        with pytest.raises(ValueError) as exc_info:
            InternalDnsServersBaseModel.validate_domain_name_not_empty([])
        assert "domain_name must not be empty" in str(exc_info.value)

        # Test valid case
        result = InternalDnsServersBaseModel.validate_domain_name_not_empty(["example.com"])
        assert result == ["example.com"]

    def test_domain_name_validator_invalid_type(self):
        """Test domain_name validator raises error for non-list, non-string type."""
        with pytest.raises(ValueError) as exc_info:
            InternalDnsServersBaseModel.validate_domain_name(123)  # Not a list or string
        assert "domain_name must be a list of strings" in str(exc_info.value)

        # Also test the full model validation
        with pytest.raises(ValidationError):
            InternalDnsServersBaseModel(
                name="test-dns-server",
                domain_name=123,
                primary="192.168.1.1",
            )

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        with pytest.raises(ValidationError):
            InternalDnsServersBaseModel()

    def test_invalid_name_pattern(self):
        """Test validation fails when name doesn't match pattern."""
        with pytest.raises(ValidationError):
            InternalDnsServersBaseModel(
                name="invalid@name",  # Invalid character
                domain_name=["example.com"],
                primary="192.168.1.1",
            )

    def test_name_too_long(self):
        """Test validation fails when name is too long."""
        with pytest.raises(ValidationError):
            InternalDnsServersBaseModel(
                name="a" * 64,  # Max length is 63
                domain_name=["example.com"],
                primary="192.168.1.1",
            )

    def test_invalid_ip_address(self):
        """Test validation fails with invalid IP address."""
        with pytest.raises(ValidationError):
            InternalDnsServersBaseModel(
                name="test-dns-server",
                domain_name=["example.com"],
                primary="not-an-ip",
            )


class TestInternalDnsServersCreateModel:
    """Tests for the InternalDnsServersCreateModel."""

    def test_valid_create_model(self):
        """Test creating a valid create model."""
        model_data = InternalDnsServersCreateModelFactory.build_valid()
        model = InternalDnsServersCreateModel(**model_data)
        assert model.name == "test-dns-server"
        assert model.domain_name == ["example.com", "test.com"]
        assert model.primary == IPv4Address("192.168.1.1")
        assert model.secondary == IPv4Address("8.8.8.8")

    def test_empty_domain_name(self):
        """Test validation fails with empty domain_name list."""
        with pytest.raises(ValidationError) as exc_info:
            model_data = InternalDnsServersCreateModelFactory.build_with_empty_domain_name()
            InternalDnsServersCreateModel(**model_data)
        assert "domain_name" in str(exc_info.value)
        assert "item" in str(exc_info.value)  # Look for min_length validation

    def test_create_model_validator(self):
        """Test the create model validator directly."""
        # Create a model with valid domain_name
        model_data = InternalDnsServersCreateModelFactory.build_valid()
        InternalDnsServersCreateModel(**model_data)

        # Create a test model with valid data
        test_model = InternalDnsServersCreateModel(**model_data)

        # Bypass validation by using object.__setattr__
        object.__setattr__(test_model, "domain_name", [])

        # Now test the validator directly
        with pytest.raises(ValueError) as exc_info:
            test_model.validate_create_model()
        assert "domain_name must not be empty" in str(exc_info.value)

    def test_secondary_optional(self):
        """Test that secondary field is optional."""
        model_data = InternalDnsServersCreateModelFactory.build_without_secondary()
        model = InternalDnsServersCreateModel(**model_data)
        assert model.secondary is None


class TestInternalDnsServersUpdateModel:
    """Tests for the InternalDnsServersUpdateModel."""

    def test_valid_update_model(self):
        """Test creating a valid update model with all fields."""
        test_id = uuid.uuid4()
        model_data = InternalDnsServersUpdateModelFactory.build_valid(id=test_id)
        model = InternalDnsServersUpdateModel(**model_data)
        assert model.id == test_id
        assert model.name == "updated-dns-server"
        assert model.domain_name == ["updated.example.com", "updated.test.com"]
        assert model.primary == IPv4Address("192.168.2.1")
        assert model.secondary == IPv4Address("8.8.4.4")

    def test_minimal_update_model(self):
        """Test creating an update model with only required fields and one update field."""
        test_id = uuid.uuid4()
        model_data = InternalDnsServersUpdateModelFactory.build_partial(
            ["name"],
            id=test_id,
            name="updated-dns-server",
        )
        model = InternalDnsServersUpdateModel(**model_data)
        assert model.id == test_id
        assert model.name == "updated-dns-server"
        assert model.domain_name is None
        assert model.primary is None
        assert model.secondary is None

    def test_missing_required_id(self):
        """Test validation fails when id is missing."""
        with pytest.raises(ValidationError):
            # Remove id from the data
            model_data = InternalDnsServersUpdateModelFactory.build_valid()
            del model_data["id"]
            InternalDnsServersUpdateModel(**model_data)

    def test_no_update_fields(self):
        """Test validation fails when no update fields are provided."""
        with pytest.raises(ValidationError) as exc_info:
            model_data = InternalDnsServersUpdateModelFactory.build_empty()
            InternalDnsServersUpdateModel(**model_data)
        assert "At least one field must be specified for update" in str(exc_info.value)

    def test_empty_domain_name(self):
        """Test validation fails with empty domain_name list."""
        with pytest.raises(ValidationError) as exc_info:
            model_data = InternalDnsServersUpdateModelFactory.build_with_empty_domain_name()
            InternalDnsServersUpdateModel(**model_data)
        assert "domain_name" in str(exc_info.value)
        assert "empty" in str(exc_info.value).lower()  # Look for 'empty' in error message

    def test_update_model_validator_empty_domain(self):
        """Test update model validator directly for empty domain_name."""
        # Create a test model with valid data
        model_data = InternalDnsServersUpdateModelFactory.build_partial(
            ["name"],
            name="updated-dns-server",
        )
        test_model = InternalDnsServersUpdateModel(**model_data)

        # Bypass validation by using object.__setattr__
        object.__setattr__(test_model, "domain_name", [])

        # Now test the validator directly
        with pytest.raises(ValueError) as exc_info:
            test_model.validate_update_model()
        assert "domain_name must not be empty if provided" in str(exc_info.value)


class TestInternalDnsServersResponseModel:
    """Tests for the InternalDnsServersResponseModel."""

    def test_valid_response_model(self):
        """Test creating a valid response model."""
        test_id = uuid.uuid4()
        model_data = InternalDnsServersResponseModelFactory.build_valid(id=test_id)
        model = InternalDnsServersResponseModel(**model_data)
        assert model.id == test_id
        assert model.name == "test-dns-server"
        assert model.domain_name == ["example.com", "test.com"]
        assert model.primary == IPv4Address("192.168.1.1")
        assert model.secondary == IPv4Address("8.8.8.8")

    def test_missing_required_id(self):
        """Test validation fails when id is missing."""
        with pytest.raises(ValidationError):
            # Remove id from the data
            model_data = InternalDnsServersResponseModelFactory.build_valid()
            del model_data["id"]
            InternalDnsServersResponseModel(**model_data)

    def test_empty_domain_name(self):
        """Test validation fails with empty domain_name list."""
        with pytest.raises(ValidationError) as exc_info:
            model_data = InternalDnsServersResponseModelFactory.build_valid()
            model_data["domain_name"] = []
            InternalDnsServersResponseModel(**model_data)
        assert "domain_name" in str(exc_info.value)
        assert "item" in str(exc_info.value)  # Look for min_length validation

    def test_response_model_validator_empty_domain(self):
        """Test response model validator directly for empty domain_name."""
        # Create a test model with valid data
        model_data = InternalDnsServersResponseModelFactory.build_valid()
        test_model = InternalDnsServersResponseModel(**model_data)

        # Bypass validation by using object.__setattr__
        object.__setattr__(test_model, "domain_name", [])

        # Now test the validator directly
        with pytest.raises(ValueError) as exc_info:
            test_model.validate_response_model()
        assert "domain_name must not be empty in response" in str(exc_info.value)
