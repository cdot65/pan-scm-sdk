# tests/scm/models/mobile_agent/test_tunnel_profiles_models.py

"""Tests for mobile agent tunnel profiles models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.mobile_agent.tunnel_profiles import (
    CookieLifetime,
    SplitTunnelingDomainEntry,
    TunnelOperatingSystem,
    TunnelProfileBaseModel,
    TunnelProfileCreateModel,
    TunnelProfileResponseModel,
    TunnelProfileUpdateModel,
)
from tests.scm.models.mobile_agent.factories import (
    TunnelProfileBaseModelFactory,
    TunnelProfileCreateModelFactory,
    TunnelProfileResponseModelFactory,
    TunnelProfileUpdateModelFactory,
)


class TestTunnelOperatingSystem:
    """Tests for the TunnelOperatingSystem enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert TunnelOperatingSystem.ANDROID == "Android"
        assert TunnelOperatingSystem.CHROME == "Chrome"
        assert TunnelOperatingSystem.IOT == "IoT"
        assert TunnelOperatingSystem.LINUX == "Linux"
        assert TunnelOperatingSystem.MAC == "Mac"
        assert TunnelOperatingSystem.WINDOWS == "Windows"
        assert TunnelOperatingSystem.WINDOWS_UWP == "WindowsUWP"
        assert TunnelOperatingSystem.IOS == "iOS"

    def test_enum_membership(self):
        """Test that the enum contains exactly the spec-defined values."""
        expected = {
            "Android",
            "Chrome",
            "IoT",
            "Linux",
            "Mac",
            "Windows",
            "WindowsUWP",
            "iOS",
        }
        assert {member.value for member in TunnelOperatingSystem} == expected


class TestTunnelProfileBaseModel:
    """Tests for TunnelProfileBaseModel validation."""

    def test_base_model_minimal(self):
        """Test that a model with only the required name field can be created."""
        model = TunnelProfileBaseModel(name="test-tunnel")
        assert model.name == "test-tunnel"
        assert model.authentication_override is None
        assert model.no_direct_access_to_local_network is None
        assert model.os is None
        assert model.retrieve_framed_ip_address is None
        assert model.source_address is None
        assert model.source_user is None
        assert model.split_tunneling is None

    def test_base_model_complete(self):
        """Test that a complete base model can be created."""
        model = TunnelProfileBaseModelFactory()
        assert model.name is not None
        assert isinstance(model.os, list)
        assert all(isinstance(os_value, TunnelOperatingSystem) for os_value in model.os)

    def test_base_model_missing_name(self):
        """Test validation when the required name field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            TunnelProfileBaseModel()
        assert "name\n  Field required" in str(exc_info.value)

    def test_base_model_empty_name(self):
        """Test validation when name is empty."""
        with pytest.raises(ValidationError) as exc_info:
            TunnelProfileBaseModel(name="")
        assert "name" in str(exc_info.value)

    def test_base_model_name_too_long(self):
        """Test validation when name exceeds the 31 character maximum."""
        with pytest.raises(ValidationError) as exc_info:
            TunnelProfileBaseModel(name="x" * 32)
        assert "name" in str(exc_info.value)

    def test_base_model_name_max_length(self):
        """Test that a 31 character name is accepted."""
        model = TunnelProfileBaseModel(name="x" * 31)
        assert len(model.name) == 31

    def test_base_model_invalid_os(self):
        """Test validation when os contains an invalid value."""
        with pytest.raises(ValidationError) as exc_info:
            TunnelProfileBaseModel(name="test-tunnel", os=["InvalidOS"])
        assert "os" in str(exc_info.value)

    def test_base_model_extra_field_forbidden(self):
        """Test that unknown fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TunnelProfileBaseModel(name="test-tunnel", unknown_field="value")
        assert "unknown_field" in str(exc_info.value)

    def test_model_dump(self):
        """Test model dumping to dictionary."""
        model = TunnelProfileBaseModelFactory()
        model_dict = model.model_dump(exclude_unset=True)
        assert model_dict["name"] == model.name
        assert model_dict["os"] == model.os


class TestNestedModels:
    """Tests for the nested tunnel profile models."""

    def test_cookie_lifetime_valid(self):
        """Test valid cookie lifetime values."""
        model = CookieLifetime(lifetime_in_hours=24)
        assert model.lifetime_in_hours == 24

    def test_cookie_lifetime_days_out_of_range(self):
        """Test that lifetime_in_days above 365 is rejected."""
        with pytest.raises(ValidationError):
            CookieLifetime(lifetime_in_days=366)

    def test_cookie_lifetime_hours_out_of_range(self):
        """Test that lifetime_in_hours above 72 is rejected."""
        with pytest.raises(ValidationError):
            CookieLifetime(lifetime_in_hours=73)

    def test_cookie_lifetime_minutes_out_of_range(self):
        """Test that lifetime_in_minutes above 59 is rejected."""
        with pytest.raises(ValidationError):
            CookieLifetime(lifetime_in_minutes=60)

    def test_cookie_lifetime_below_minimum(self):
        """Test that values below 1 are rejected."""
        with pytest.raises(ValidationError):
            CookieLifetime(lifetime_in_days=0)

    def test_domain_entry_valid_ports(self):
        """Test valid domain entry ports."""
        model = SplitTunnelingDomainEntry(name="example.com", ports=[80, 443])
        assert model.ports == [80, 443]

    def test_domain_entry_port_too_large(self):
        """Test that a port above 65535 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SplitTunnelingDomainEntry(name="example.com", ports=[65536])
        assert "Ports must be between 1 and 65535" in str(exc_info.value)

    def test_domain_entry_port_too_small(self):
        """Test that a port below 1 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SplitTunnelingDomainEntry(name="example.com", ports=[0])
        assert "Ports must be between 1 and 65535" in str(exc_info.value)


class TestTunnelProfileCreateModel:
    """Tests for TunnelProfileCreateModel validation."""

    def test_create_model_valid(self):
        """Test that a valid create model can be built."""
        data = TunnelProfileCreateModelFactory.build_valid()
        model = TunnelProfileCreateModel(**data)
        assert model.name == data["name"]

    def test_create_model_valid_full(self):
        """Test that a create model with all nested structures can be built."""
        data = TunnelProfileCreateModelFactory.build_valid_full()
        model = TunnelProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.authentication_override.accept_cookie.generate_cookie is True
        assert model.authentication_override.accept_cookie.cookie_lifetime.lifetime_in_hours == 24
        assert model.source_address.ip_address == ["10.0.0.0/24"]
        assert model.split_tunneling.access_route == ["10.1.0.0/16"]
        assert model.split_tunneling.exclude_domains.list[0].name == "example.com"
        assert model.split_tunneling.include_domains.list[0].ports == [80, 443]

    def test_create_model_invalid_name(self):
        """Test validation when name is too long."""
        data = TunnelProfileCreateModelFactory.build_invalid_name()
        with pytest.raises(ValidationError):
            TunnelProfileCreateModel(**data)

    def test_create_model_invalid_os(self):
        """Test validation when os contains an invalid value."""
        data = TunnelProfileCreateModelFactory.build_invalid_os()
        with pytest.raises(ValidationError):
            TunnelProfileCreateModel(**data)

    def test_create_model_dump_excludes_unset(self):
        """Test that unset fields are excluded from the payload."""
        model = TunnelProfileCreateModel(name="test-tunnel")
        payload = model.model_dump(exclude_unset=True)
        assert payload == {"name": "test-tunnel"}


class TestTunnelProfileUpdateModel:
    """Tests for TunnelProfileUpdateModel validation."""

    def test_update_model_valid(self):
        """Test that a valid update model can be built."""
        data = TunnelProfileUpdateModelFactory.build_valid()
        model = TunnelProfileUpdateModel(**data)
        assert model.name == data["name"]

    def test_update_model_requires_name(self):
        """Test that the update model requires a name (name-addressed resource)."""
        with pytest.raises(ValidationError) as exc_info:
            TunnelProfileUpdateModel(os=[TunnelOperatingSystem.LINUX])
        assert "name\n  Field required" in str(exc_info.value)


class TestTunnelProfileResponseModel:
    """Tests for TunnelProfileResponseModel validation."""

    def test_response_model_valid(self):
        """Test that a valid response model can be built."""
        model = TunnelProfileResponseModelFactory()
        assert model.name is not None
        assert model.folder == "Mobile Users"

    def test_response_model_ignores_extra_fields(self):
        """Test that unknown fields in API responses are ignored."""
        model = TunnelProfileResponseModel(
            name="test-tunnel",
            folder="Mobile Users",
            unexpected_api_field="ignored",
        )
        assert model.name == "test-tunnel"
        assert not hasattr(model, "unexpected_api_field")

    def test_response_model_without_folder(self):
        """Test that the response model works without a folder field."""
        model = TunnelProfileResponseModel(name="test-tunnel")
        assert model.folder is None
