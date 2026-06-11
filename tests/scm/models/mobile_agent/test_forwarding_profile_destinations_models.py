# tests/scm/models/mobile_agent/test_forwarding_profile_destinations_models.py

"""Tests for mobile agent forwarding profile destination models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.mobile_agent.forwarding_profile_destinations import (
    DestinationFqdnEntry,
    DestinationIpEntry,
    ForwardingProfileDestinationBaseModel,
    ForwardingProfileDestinationCreateModel,
    ForwardingProfileDestinationResponseModel,
    ForwardingProfileDestinationUpdateModel,
)
from tests.scm.models.mobile_agent.factories import (
    DestinationFqdnEntryFactory,
    DestinationIpEntryFactory,
    ForwardingProfileDestinationCreateModelFactory,
    ForwardingProfileDestinationResponseModelFactory,
    ForwardingProfileDestinationUpdateModelFactory,
)


class TestDestinationFqdnEntry:
    """Tests for DestinationFqdnEntry validation."""

    def test_entry_valid(self):
        """Test that a valid FQDN entry can be created."""
        entry = DestinationFqdnEntry(name="www.example.com", port=443)
        assert entry.name == "www.example.com"
        assert entry.port == 443

    def test_entry_factory(self):
        """Test that the factory builds a valid entry."""
        entry = DestinationFqdnEntryFactory()
        assert entry.name is not None
        assert 1 <= entry.port <= 65535

    def test_entry_wildcard_and_dollar(self):
        """Test that wildcards and a trailing $ are accepted."""
        assert DestinationFqdnEntry(name="*.example.com").name == "*.example.com"
        assert DestinationFqdnEntry(name="example.com$").name == "example.com$"

    def test_entry_port_optional(self):
        """Test that port is optional."""
        entry = DestinationFqdnEntry(name="www.example.com")
        assert entry.port is None

    def test_entry_invalid_name(self):
        """Test validation when the FQDN has invalid characters."""
        with pytest.raises(ValidationError) as exc_info:
            DestinationFqdnEntry(name="invalid name")
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_entry_invalid_port(self):
        """Test validation when the port is out of range."""
        with pytest.raises(ValidationError):
            DestinationFqdnEntry(name="www.example.com", port=0)
        with pytest.raises(ValidationError):
            DestinationFqdnEntry(name="www.example.com", port=65536)


class TestDestinationIpEntry:
    """Tests for DestinationIpEntry validation."""

    def test_entry_valid(self):
        """Test that a valid IP entry can be created."""
        entry = DestinationIpEntry(name="192.168.1.1", port=8080)
        assert entry.name == "192.168.1.1"
        assert entry.port == 8080

    def test_entry_factory(self):
        """Test that the factory builds a valid entry."""
        entry = DestinationIpEntryFactory()
        assert entry.name is not None

    def test_entry_cidr_notation(self):
        """Test that CIDR notation is accepted."""
        entry = DestinationIpEntry(name="10.0.0.0/8")
        assert entry.name == "10.0.0.0/8"

    def test_entry_wildcards(self):
        """Test that wildcard octets are accepted."""
        entry = DestinationIpEntry(name="192.168.1.*")
        assert entry.name == "192.168.1.*"

    def test_entry_invalid_ip(self):
        """Test validation when the IP address is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            DestinationIpEntry(name="999.999.999.999")
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_entry_invalid_port(self):
        """Test validation when the port is out of range."""
        with pytest.raises(ValidationError):
            DestinationIpEntry(name="192.168.1.1", port=70000)


class TestForwardingProfileDestinationBaseModel:
    """Tests for ForwardingProfileDestinationBaseModel validation."""

    def test_base_model_minimal(self):
        """Test that a minimal base model can be created."""
        model = ForwardingProfileDestinationBaseModel(name="test-destination")
        assert model.name == "test-destination"
        assert model.description is None
        assert model.fqdn is None
        assert model.ip_addresses is None

    def test_base_model_complete(self):
        """Test that a complete base model can be created."""
        model = ForwardingProfileDestinationBaseModel(
            name="test-destination",
            description="Test destination",
            fqdn=[{"name": "*.example.com", "port": 443}],
            ip_addresses=[{"name": "10.0.0.0/8"}],
        )
        assert isinstance(model.fqdn[0], DestinationFqdnEntry)
        assert isinstance(model.ip_addresses[0], DestinationIpEntry)

    def test_base_model_missing_name(self):
        """Test validation when name is missing."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileDestinationBaseModel()
        assert "name\n  Field required" in str(exc_info.value)

    def test_base_model_invalid_name(self):
        """Test validation when name has invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileDestinationBaseModel(name="invalid@name")
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_base_model_name_too_long(self):
        """Test validation when name exceeds max length."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileDestinationBaseModel(name="a" * 65)
        assert "name\n  String should have at most 64 characters" in str(exc_info.value)


class TestForwardingProfileDestinationCreateModel:
    """Tests for ForwardingProfileDestinationCreateModel validation."""

    def test_create_model_valid(self):
        """Test that valid create data is accepted."""
        data = ForwardingProfileDestinationCreateModelFactory.build_valid()
        model = ForwardingProfileDestinationCreateModel(**data)
        assert model.name == data["name"]
        assert model.fqdn[0].name == "*.example.com"

    def test_create_model_invalid_name(self):
        """Test validation when name has invalid format."""
        data = ForwardingProfileDestinationCreateModelFactory.build_invalid_name()
        with pytest.raises(ValidationError):
            ForwardingProfileDestinationCreateModel(**data)

    def test_create_model_no_folder_field(self):
        """Test that folder is rejected in the body (query parameter only)."""
        data = ForwardingProfileDestinationCreateModelFactory.build_valid()
        data["folder"] = "Mobile Users"
        with pytest.raises(ValidationError):
            ForwardingProfileDestinationCreateModel(**data)

    def test_create_model_dump_excludes_unset(self):
        """Test that unset fields are excluded from the payload."""
        model = ForwardingProfileDestinationCreateModel(name="test-destination")
        payload = model.model_dump(exclude_unset=True)
        assert payload == {"name": "test-destination"}


class TestForwardingProfileDestinationUpdateModel:
    """Tests for ForwardingProfileDestinationUpdateModel validation."""

    def test_update_model_valid(self):
        """Test that valid update data is accepted."""
        data = ForwardingProfileDestinationUpdateModelFactory.build_valid()
        model = ForwardingProfileDestinationUpdateModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]

    def test_update_model_without_id(self):
        """Test that the update model does not require an id."""
        model = ForwardingProfileDestinationUpdateModel(name="test-destination")
        assert model.id is None

    def test_update_model_requires_name(self):
        """Test that the update model requires a name, per the API schema."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileDestinationUpdateModel(description="no name")
        assert "name\n  Field required" in str(exc_info.value)


class TestForwardingProfileDestinationResponseModel:
    """Tests for ForwardingProfileDestinationResponseModel validation."""

    def test_response_model_valid(self):
        """Test that a response model can be created."""
        model = ForwardingProfileDestinationResponseModelFactory()
        assert model.id is not None
        assert model.name is not None

    def test_response_model_ignores_extra_fields(self):
        """Test that unknown response fields are ignored."""
        model = ForwardingProfileDestinationResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-destination",
            unknown_api_field="ignored",
        )
        assert model.name == "test-destination"
        assert not hasattr(model, "unknown_api_field")

    def test_response_model_without_id(self):
        """Test that a response without an id is tolerated."""
        model = ForwardingProfileDestinationResponseModel(name="test-destination")
        assert model.id is None
