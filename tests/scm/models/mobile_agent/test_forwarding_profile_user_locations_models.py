# tests/scm/models/mobile_agent/test_forwarding_profile_user_locations_models.py

"""Tests for forwarding profile user location models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.mobile_agent.forwarding_profile_user_locations import (
    ForwardingProfileUserLocationBaseModel,
    ForwardingProfileUserLocationCreateModel,
    ForwardingProfileUserLocationResponseModel,
    ForwardingProfileUserLocationUpdateModel,
    UserLocationChoice,
    UserLocationInternalHostDetection,
    UserLocationIpEntry,
)
from tests.scm.models.mobile_agent.factories import (
    ForwardingProfileUserLocationCreateModelFactory,
    ForwardingProfileUserLocationResponseModelFactory,
)

TEST_ID = "123e4567-e89b-12d3-a456-426655440000"


class TestUserLocationIpEntry:
    """Tests for UserLocationIpEntry validation."""

    def test_valid_ip(self):
        """Test a valid plain IPv4 address."""
        entry = UserLocationIpEntry(name="10.1.2.3")
        assert entry.name == "10.1.2.3"

    def test_valid_cidr(self):
        """Test a valid IPv4 CIDR."""
        entry = UserLocationIpEntry(name="10.0.0.0/8")
        assert entry.name == "10.0.0.0/8"

    def test_valid_wildcard(self):
        """Test a valid wildcard address."""
        entry = UserLocationIpEntry(name="10.1.*.*")
        assert entry.name == "10.1.*.*"

    def test_invalid_ip(self):
        """Test that an out-of-range octet is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserLocationIpEntry(name="999.1.1.1")
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_missing_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            UserLocationIpEntry()
        assert "name\n  Field required" in str(exc_info.value)


class TestUserLocationInternalHostDetection:
    """Tests for UserLocationInternalHostDetection validation."""

    def test_valid(self):
        """Test valid internal host detection settings."""
        ihd = UserLocationInternalHostDetection(
            ip_address="10.0.0.1",
            fqdn="internal.example.com",
        )
        assert ihd.ip_address == "10.0.0.1"
        assert ihd.fqdn == "internal.example.com"

    def test_invalid_ip_address(self):
        """Test that an invalid IP address is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserLocationInternalHostDetection(ip_address="not-an-ip")
        assert "ip_address\n  String should match pattern" in str(exc_info.value)

    def test_invalid_fqdn(self):
        """Test that an invalid FQDN is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserLocationInternalHostDetection(fqdn="bad fqdn!")
        assert "fqdn\n  String should match pattern" in str(exc_info.value)

    def test_fqdn_too_long(self):
        """Test FQDN length validation."""
        with pytest.raises(ValidationError) as exc_info:
            UserLocationInternalHostDetection(fqdn="a" * 256)
        assert "fqdn\n  String should have at most 255 characters" in str(exc_info.value)


class TestUserLocationChoice:
    """Tests for UserLocationChoice validation."""

    def test_valid_with_ip_addresses(self):
        """Test a choice with IP address entries."""
        choice = UserLocationChoice(ip_addresses=[{"name": "10.0.0.0/8"}])
        assert choice.ip_addresses is not None
        assert choice.internal_host_detection is None

    def test_valid_with_internal_host_detection(self):
        """Test a choice with internal host detection."""
        choice = UserLocationChoice(
            internal_host_detection={"fqdn": "internal.example.com"},
        )
        assert choice.internal_host_detection is not None
        assert choice.ip_addresses is None

    def test_both_options_rejected(self):
        """Test that providing both options raises an error."""
        with pytest.raises(ValidationError) as exc_info:
            UserLocationChoice(
                internal_host_detection={"fqdn": "internal.example.com"},
                ip_addresses=[{"name": "10.0.0.0/8"}],
            )
        assert "Exactly one of 'internal_host_detection' or 'ip_addresses'" in str(exc_info.value)

    def test_no_options_rejected(self):
        """Test that providing no options raises an error."""
        with pytest.raises(ValidationError) as exc_info:
            UserLocationChoice()
        assert "Exactly one of 'internal_host_detection' or 'ip_addresses'" in str(exc_info.value)


class TestForwardingProfileUserLocationBaseModel:
    """Tests for ForwardingProfileUserLocationBaseModel validation."""

    def test_base_model_valid(self):
        """Test that a valid base model can be created."""
        model = ForwardingProfileUserLocationBaseModel(
            name="branch-offices",
            choice={"ip_addresses": [{"name": "10.1.0.0/16"}]},
        )
        assert model.name == "branch-offices"
        assert model.choice.ip_addresses[0].name == "10.1.0.0/16"

    def test_base_model_invalid_name(self):
        """Test validation when name has invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileUserLocationBaseModel(
                name="invalid name!",
                choice={"ip_addresses": [{"name": "10.1.0.0/16"}]},
            )
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_base_model_missing_choice(self):
        """Test validation when choice is missing."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileUserLocationBaseModel(name="branch-offices")
        assert "choice\n  Field required" in str(exc_info.value)

    def test_base_model_rejects_extra_fields(self):
        """Test that unknown fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileUserLocationBaseModel(
                name="branch-offices",
                choice={"ip_addresses": [{"name": "10.1.0.0/16"}]},
                unknown_field="value",
            )
        assert "unknown_field" in str(exc_info.value)


class TestForwardingProfileUserLocationCreateModel:
    """Tests for ForwardingProfileUserLocationCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = ForwardingProfileUserLocationCreateModelFactory.build_valid()
        model = ForwardingProfileUserLocationCreateModel(**data)
        assert model.name == data["name"]
        assert model.choice.ip_addresses is not None

    def test_create_model_dump_round_trip(self):
        """Test that model_dump produces API-compatible payloads."""
        model = ForwardingProfileUserLocationCreateModel(
            name="corporate-network",
            choice={"internal_host_detection": {"ip_address": "10.0.0.1"}},
        )
        payload = model.model_dump(exclude_unset=True)
        assert payload == {
            "name": "corporate-network",
            "choice": {"internal_host_detection": {"ip_address": "10.0.0.1"}},
        }


class TestForwardingProfileUserLocationUpdateModel:
    """Tests for ForwardingProfileUserLocationUpdateModel validation."""

    def test_update_model_requires_id(self):
        """Test that the update model requires an id."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileUserLocationUpdateModel(
                name="branch-offices",
                choice={"ip_addresses": [{"name": "10.1.0.0/16"}]},
            )
        assert "id\n  Field required" in str(exc_info.value)

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        model = ForwardingProfileUserLocationUpdateModel(
            id=TEST_ID,
            name="branch-offices",
            choice={"ip_addresses": [{"name": "10.1.0.0/16"}]},
        )
        assert str(model.id) == TEST_ID


class TestForwardingProfileUserLocationResponseModel:
    """Tests for ForwardingProfileUserLocationResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        model = ForwardingProfileUserLocationResponseModel(
            id=TEST_ID,
            name="branch-offices",
            choice={"ip_addresses": [{"name": "10.1.0.0/16"}]},
        )
        assert str(model.id) == TEST_ID

    def test_response_model_from_factory(self):
        """Test that the response model factory produces valid models."""
        model = ForwardingProfileUserLocationResponseModelFactory()
        assert model.name is not None
        assert model.id is not None

    def test_response_model_ignores_extra_fields(self):
        """Test that unknown fields in API responses are ignored."""
        model = ForwardingProfileUserLocationResponseModel(
            id=TEST_ID,
            name="branch-offices",
            choice={"ip_addresses": [{"name": "10.1.0.0/16"}]},
            future_field="ignored",
        )
        assert not hasattr(model, "future_field")
