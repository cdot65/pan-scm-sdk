# tests/scm/models/mobile_agent/test_forwarding_profile_regional_and_custom_proxies_models.py

"""Tests for forwarding profile regional and custom proxy models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.mobile_agent.forwarding_profile_regional_and_custom_proxies import (
    ForwardingProfileRegionalAndCustomProxyBaseModel,
    ForwardingProfileRegionalAndCustomProxyCreateModel,
    ForwardingProfileRegionalAndCustomProxyResponseModel,
    ForwardingProfileRegionalAndCustomProxyUpdateModel,
    RegionalProxyConnectivityName,
    RegionalProxyConnectivityPreference,
    RegionalProxyFallbackOption,
    RegionalProxyLocationPreference,
    RegionalProxyPrismaAccessLocation,
    RegionalProxyServer,
    RegionalProxyType,
)
from tests.scm.models.mobile_agent.factories import (
    ForwardingProfileRegionalAndCustomProxyCreateModelFactory,
    ForwardingProfileRegionalAndCustomProxyResponseModelFactory,
)

TEST_ID = "123e4567-e89b-12d3-a456-426655440000"


class TestRegionalProxyEnums:
    """Tests for the regional and custom proxy enums."""

    def test_proxy_type_values(self):
        """Test that the RegionalProxyType enum has the expected values."""
        assert RegionalProxyType.GP_AND_PAC == "gp-and-pac"
        assert RegionalProxyType.ZTNA_AGENT == "ztna-agent"

    def test_connectivity_name_values(self):
        """Test that the RegionalProxyConnectivityName enum has the expected values."""
        assert RegionalProxyConnectivityName.TUNNEL == "tunnel"
        assert RegionalProxyConnectivityName.PROXY == "proxy"
        assert RegionalProxyConnectivityName.ADNS == "adns"
        assert RegionalProxyConnectivityName.MASQUE == "masque"

    def test_fallback_option_values(self):
        """Test that the RegionalProxyFallbackOption enum has the expected values."""
        assert RegionalProxyFallbackOption.FAIL_OPEN == "fail-open"
        assert RegionalProxyFallbackOption.FAIL_SAFE == "fail-safe"

    def test_location_preference_values(self):
        """Test that the RegionalProxyLocationPreference enum has the expected values."""
        assert RegionalProxyLocationPreference.BEST_AVAILABLE == "best-available-pa-location"
        assert RegionalProxyLocationPreference.SPECIFIC == "specific-pa-location"


class TestRegionalProxyServer:
    """Tests for RegionalProxyServer validation."""

    def test_valid(self):
        """Test a valid proxy server."""
        server = RegionalProxyServer(
            fqdn="proxy1.example.com",
            port=8080,
            location="Frankfurt",
        )
        assert server.fqdn == "proxy1.example.com"
        assert server.port == 8080
        assert server.location == "Frankfurt"

    def test_invalid_fqdn(self):
        """Test that an invalid FQDN is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegionalProxyServer(fqdn="bad fqdn!")
        assert "fqdn\n  String should match pattern" in str(exc_info.value)

    def test_port_too_low(self):
        """Test that port 0 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegionalProxyServer(port=0)
        assert "port\n  Input should be greater than or equal to 1" in str(exc_info.value)

    def test_port_too_high(self):
        """Test that port 65536 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegionalProxyServer(port=65536)
        assert "port\n  Input should be less than or equal to 65535" in str(exc_info.value)


class TestRegionalProxyConnectivityPreference:
    """Tests for RegionalProxyConnectivityPreference validation."""

    def test_valid(self):
        """Test a valid connectivity preference."""
        pref = RegionalProxyConnectivityPreference(name="tunnel", enabled=True)
        assert pref.name == RegionalProxyConnectivityName.TUNNEL
        assert pref.enabled is True

    def test_invalid_name(self):
        """Test that an invalid connectivity preference name is rejected."""
        with pytest.raises(ValidationError):
            RegionalProxyConnectivityPreference(name="vpn")

    def test_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            RegionalProxyConnectivityPreference()
        assert "name\n  Field required" in str(exc_info.value)


class TestRegionalProxyPrismaAccessLocation:
    """Tests for RegionalProxyPrismaAccessLocation validation."""

    def test_valid(self):
        """Test a valid Prisma Access location entry."""
        location = RegionalProxyPrismaAccessLocation(
            name="europe",
            locations=["frankfurt", "paris"],
        )
        assert location.name == "europe"
        assert location.locations == ["frankfurt", "paris"]

    def test_invalid_name(self):
        """Test that a region name with invalid characters is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegionalProxyPrismaAccessLocation(name="europe-1")
        assert "name\n  String should match pattern" in str(exc_info.value)


class TestForwardingProfileRegionalAndCustomProxyBaseModel:
    """Tests for ForwardingProfileRegionalAndCustomProxyBaseModel validation."""

    def test_base_model_minimal(self):
        """Test that a minimal base model defaults type to gp-and-pac."""
        model = ForwardingProfileRegionalAndCustomProxyBaseModel(name="emea-proxy")
        assert model.name == "emea-proxy"
        assert model.type == RegionalProxyType.GP_AND_PAC
        assert model.proxy_1 is None

    def test_base_model_complete(self):
        """Test that a complete base model can be created."""
        model = ForwardingProfileRegionalAndCustomProxyBaseModel(
            name="emea-proxy",
            type="ztna-agent",
            description="EMEA regional proxy",
            proxy_1={"fqdn": "proxy1.example.com", "port": 8080},
            proxy_2={"fqdn": "proxy2.example.com", "port": 8443},
            connectivity_preference=[{"name": "tunnel", "enabled": True}],
            fallback_option="fail-open",
            location_preference="specific-pa-location",
            prisma_access_locations=[{"name": "europe", "locations": ["frankfurt"]}],
        )
        assert model.type == RegionalProxyType.ZTNA_AGENT
        assert model.proxy_1.port == 8080
        assert model.connectivity_preference[0].name == RegionalProxyConnectivityName.TUNNEL
        assert model.fallback_option == RegionalProxyFallbackOption.FAIL_OPEN
        assert model.location_preference == RegionalProxyLocationPreference.SPECIFIC
        assert model.prisma_access_locations[0].name == "europe"

    def test_base_model_invalid_name(self):
        """Test validation when name has invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileRegionalAndCustomProxyBaseModel(name="invalid name!")
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_base_model_invalid_type(self):
        """Test validation when type is invalid."""
        with pytest.raises(ValidationError):
            ForwardingProfileRegionalAndCustomProxyBaseModel(
                name="emea-proxy",
                type="invalid-type",
            )

    def test_base_model_rejects_extra_fields(self):
        """Test that unknown fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileRegionalAndCustomProxyBaseModel(
                name="emea-proxy",
                unknown_field="value",
            )
        assert "unknown_field" in str(exc_info.value)

    def test_model_dump_exclude_unset(self):
        """Test model dumping with exclude_unset omits defaults."""
        model = ForwardingProfileRegionalAndCustomProxyBaseModel(name="emea-proxy")
        model_dict = model.model_dump(exclude_unset=True)
        assert model_dict == {"name": "emea-proxy"}


class TestForwardingProfileRegionalAndCustomProxyCreateModel:
    """Tests for ForwardingProfileRegionalAndCustomProxyCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = ForwardingProfileRegionalAndCustomProxyCreateModelFactory.build_valid()
        model = ForwardingProfileRegionalAndCustomProxyCreateModel(**data)
        assert model.name == data["name"]
        assert model.proxy_1 is not None


class TestForwardingProfileRegionalAndCustomProxyUpdateModel:
    """Tests for ForwardingProfileRegionalAndCustomProxyUpdateModel validation."""

    def test_update_model_requires_id(self):
        """Test that the update model requires an id."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileRegionalAndCustomProxyUpdateModel(name="emea-proxy")
        assert "id\n  Field required" in str(exc_info.value)

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        model = ForwardingProfileRegionalAndCustomProxyUpdateModel(
            id=TEST_ID,
            name="emea-proxy",
            fallback_option="fail-safe",
        )
        assert str(model.id) == TEST_ID
        assert model.fallback_option == RegionalProxyFallbackOption.FAIL_SAFE


class TestForwardingProfileRegionalAndCustomProxyResponseModel:
    """Tests for ForwardingProfileRegionalAndCustomProxyResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        model = ForwardingProfileRegionalAndCustomProxyResponseModel(
            id=TEST_ID,
            name="emea-proxy",
        )
        assert str(model.id) == TEST_ID

    def test_response_model_from_factory(self):
        """Test that the response model factory produces valid models."""
        model = ForwardingProfileRegionalAndCustomProxyResponseModelFactory()
        assert model.name is not None
        assert model.id is not None

    def test_response_model_ignores_extra_fields(self):
        """Test that unknown fields in API responses are ignored."""
        model = ForwardingProfileRegionalAndCustomProxyResponseModel(
            id=TEST_ID,
            name="emea-proxy",
            future_field="ignored",
        )
        assert not hasattr(model, "future_field")
