# tests/scm/models/mobile_agent/test_forwarding_profiles_models.py

"""Tests for mobile agent forwarding profile models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.mobile_agent.forwarding_profiles import (
    BasicForwardingConfig,
    BlockRuleBasic,
    BlockRuleZtna,
    DefinitionMethod,
    ForwardingProfileBaseModel,
    ForwardingProfileCreateModel,
    ForwardingProfileGlobalProtectProxy,
    ForwardingProfilePacFile,
    ForwardingProfileResponseModel,
    ForwardingProfileUpdateModel,
    ForwardingProfileZtnaAgent,
    ForwardingRuleBasic,
    ForwardingRuleZtna,
    ZtnaForwardingConfig,
    ZtnaTrafficType,
)
from tests.scm.models.mobile_agent.factories import (
    ForwardingProfileCreateModelFactory,
    ForwardingProfileResponseModelFactory,
    ForwardingProfileUpdateModelFactory,
    ForwardingRuleBasicFactory,
    ForwardingRuleZtnaFactory,
)


class TestDefinitionMethod:
    """Tests for the DefinitionMethod enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert DefinitionMethod.RULES == "rules"
        assert DefinitionMethod.PAC_FILE == "pac-file"


class TestZtnaTrafficType:
    """Tests for the ZtnaTrafficType enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert ZtnaTrafficType.DNS == "dns"
        assert ZtnaTrafficType.DNS_AND_NETWORK_TRAFFIC == "dns-and-network-traffic"
        assert ZtnaTrafficType.NETWORK_TRAFFIC == "network-traffic"


class TestForwardingRuleBasic:
    """Tests for ForwardingRuleBasic validation."""

    def test_rule_defaults(self):
        """Test that spec defaults are applied."""
        rule = ForwardingRuleBasic(name="test-rule")
        assert rule.enabled is True
        assert rule.user_locations == "Any"
        assert rule.destinations == "Any"
        assert rule.connectivity == "direct"

    def test_rule_factory(self):
        """Test that the factory builds a valid rule."""
        rule = ForwardingRuleBasicFactory()
        assert rule.name is not None

    def test_rule_missing_name(self):
        """Test validation when name is missing."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingRuleBasic()
        assert "name\n  Field required" in str(exc_info.value)

    def test_rule_invalid_name(self):
        """Test validation when name has invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingRuleBasic(name="invalid@name")
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_rule_extra_field_rejected(self):
        """Test that unknown fields are rejected."""
        with pytest.raises(ValidationError):
            ForwardingRuleBasic(name="test-rule", unknown_field="value")


class TestForwardingRuleZtna:
    """Tests for ForwardingRuleZtna validation."""

    def test_rule_defaults(self):
        """Test that spec defaults are applied."""
        rule = ForwardingRuleZtna(name="test-rule")
        assert rule.traffic_type == ZtnaTrafficType.DNS
        assert rule.enabled is True
        assert rule.user_locations == "Any"
        assert rule.source_applications == "Any"
        assert rule.destinations == "Any"
        assert rule.connectivity == "direct"

    def test_rule_factory(self):
        """Test that the factory builds a valid rule."""
        rule = ForwardingRuleZtnaFactory()
        assert rule.name is not None
        assert rule.traffic_type in list(ZtnaTrafficType)

    def test_rule_invalid_traffic_type(self):
        """Test validation when traffic_type is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingRuleZtna(name="test-rule", traffic_type="invalid")
        assert "traffic_type" in str(exc_info.value)


class TestBlockRules:
    """Tests for the basic and ZTNA block rule models."""

    def test_block_rule_basic(self):
        """Test that a basic block rule validates nested allow settings."""
        rule = BlockRuleBasic(
            enable=True,
            allow_tcp={"enable_locations": True, "locations": ["us-east"]},
            allow_udp={
                "enable_locations": True,
                "enable_destinations": True,
                "locations": ["us-west"],
                "destinations": "dns-servers",
            },
        )
        assert rule.enable is True
        assert rule.allow_tcp.locations == ["us-east"]
        assert rule.allow_udp.destinations == "dns-servers"

    def test_block_rule_ztna_defaults(self):
        """Test that ZTNA block rule spec defaults are applied."""
        rule = BlockRuleZtna()
        assert rule.block_all_other_unmatched_outbound_connections is False
        assert rule.block_outbound_lan_access_when_connected_to_tunnel is False
        assert rule.block_inbound_access_when_connected_to_tunnel is False
        assert rule.block_non_tcp_non_udp_based_traffic_when_connected_to_tunnel is False
        assert rule.allow_icmp_for_troubleshooting is False
        assert rule.enforcer_fqdn_dns_resolution_via_dns_servers is True
        assert rule.resolve_all_fqdns_using_dns_servers_assigned_by_the_tunnel is True


class TestForwardingProfileTypeVariants:
    """Tests for the oneOf type variants of the forwarding profile."""

    def test_pac_file_variant(self):
        """Test that a pac_file dict resolves to ForwardingProfilePacFile."""
        model = ForwardingProfileBaseModel(
            name="test-profile",
            type={"pac_file": {"pac_upload": True}},
        )
        assert isinstance(model.type, ForwardingProfilePacFile)
        assert model.type.pac_file.pac_upload is True

    def test_global_protect_proxy_variant(self):
        """Test that a global_protect_proxy dict resolves to ForwardingProfileGlobalProtectProxy."""
        model = ForwardingProfileBaseModel(
            name="test-profile",
            type={
                "global_protect_proxy": {
                    "forwarding_rules": [{"name": "rule1"}],
                    "block_rule": {"enable": True},
                }
            },
        )
        assert isinstance(model.type, ForwardingProfileGlobalProtectProxy)
        assert isinstance(model.type.global_protect_proxy, BasicForwardingConfig)
        assert model.type.global_protect_proxy.forwarding_rules[0].name == "rule1"

    def test_ztna_agent_variant(self):
        """Test that a ztna_agent dict resolves to ForwardingProfileZtnaAgent."""
        model = ForwardingProfileBaseModel(
            name="test-profile",
            type={
                "ztna_agent": {
                    "forwarding_rules": [
                        {"name": "rule1", "traffic_type": "dns-and-network-traffic"}
                    ],
                    "block_rule": {"allow_icmp_for_troubleshooting": True},
                }
            },
        )
        assert isinstance(model.type, ForwardingProfileZtnaAgent)
        assert isinstance(model.type.ztna_agent, ZtnaForwardingConfig)
        assert (
            model.type.ztna_agent.forwarding_rules[0].traffic_type
            == ZtnaTrafficType.DNS_AND_NETWORK_TRAFFIC
        )

    def test_invalid_type_variant(self):
        """Test validation when the type does not match any variant."""
        with pytest.raises(ValidationError):
            ForwardingProfileBaseModel(
                name="test-profile",
                type={"unknown_variant": {}},
            )


class TestForwardingProfileBaseModel:
    """Tests for ForwardingProfileBaseModel validation."""

    def test_base_model_minimal(self):
        """Test that a minimal base model can be created."""
        model = ForwardingProfileBaseModel(name="test-profile")
        assert model.name == "test-profile"
        assert model.definition_method == DefinitionMethod.RULES
        assert model.description is None
        assert model.type is None

    def test_base_model_missing_name(self):
        """Test validation when name is missing."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileBaseModel()
        assert "name\n  Field required" in str(exc_info.value)

    def test_base_model_invalid_name(self):
        """Test validation when name has invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileBaseModel(name="invalid name with spaces")
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_base_model_name_too_long(self):
        """Test validation when name exceeds max length."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileBaseModel(name="a" * 65)
        assert "name\n  String should have at most 64 characters" in str(exc_info.value)

    def test_base_model_description_too_long(self):
        """Test validation when description exceeds max length."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileBaseModel(name="test-profile", description="a" * 1024)
        assert "description\n  String should have at most 1023 characters" in str(exc_info.value)

    def test_base_model_invalid_definition_method(self):
        """Test validation when definition_method is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileBaseModel(name="test-profile", definition_method="invalid")
        assert "definition_method" in str(exc_info.value)


class TestForwardingProfileCreateModel:
    """Tests for ForwardingProfileCreateModel validation."""

    def test_create_model_valid(self):
        """Test that valid create data is accepted."""
        data = ForwardingProfileCreateModelFactory.build_valid()
        model = ForwardingProfileCreateModel(**data)
        assert model.name == data["name"]
        assert isinstance(model.type, ForwardingProfileZtnaAgent)

    def test_create_model_invalid_name(self):
        """Test validation when name has invalid format."""
        data = ForwardingProfileCreateModelFactory.build_invalid_name()
        with pytest.raises(ValidationError):
            ForwardingProfileCreateModel(**data)

    def test_create_model_no_folder_field(self):
        """Test that folder is rejected in the body (query parameter only)."""
        data = ForwardingProfileCreateModelFactory.build_valid()
        data["folder"] = "Mobile Users"
        with pytest.raises(ValidationError):
            ForwardingProfileCreateModel(**data)

    def test_create_model_dump_excludes_unset(self):
        """Test that unset fields are excluded from the payload."""
        model = ForwardingProfileCreateModel(name="test-profile")
        payload = model.model_dump(exclude_unset=True)
        assert payload == {"name": "test-profile"}


class TestForwardingProfileUpdateModel:
    """Tests for ForwardingProfileUpdateModel validation."""

    def test_update_model_valid(self):
        """Test that valid update data is accepted."""
        data = ForwardingProfileUpdateModelFactory.build_valid()
        model = ForwardingProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]

    def test_update_model_without_id(self):
        """Test that the update model does not require an id."""
        model = ForwardingProfileUpdateModel(name="test-profile")
        assert model.id is None

    def test_update_model_requires_name(self):
        """Test that the update model requires a name, per the API schema."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileUpdateModel(description="no name")
        assert "name\n  Field required" in str(exc_info.value)


class TestForwardingProfileResponseModel:
    """Tests for ForwardingProfileResponseModel validation."""

    def test_response_model_valid(self):
        """Test that a response model can be created."""
        model = ForwardingProfileResponseModelFactory()
        assert model.id is not None
        assert model.name is not None

    def test_response_model_ignores_extra_fields(self):
        """Test that unknown response fields are ignored."""
        model = ForwardingProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-profile",
            unknown_api_field="ignored",
        )
        assert model.name == "test-profile"
        assert not hasattr(model, "unknown_api_field")

    def test_response_model_without_id(self):
        """Test that a response without an id is tolerated."""
        model = ForwardingProfileResponseModel(name="test-profile")
        assert model.id is None
