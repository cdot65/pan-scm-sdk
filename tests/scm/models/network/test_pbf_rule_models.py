"""Test models for PBF Rules."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    PbfRuleAction,
    PbfRuleBaseModel,
    PbfRuleCreateModel,
    PbfRuleEnforceSymmetricReturn,
    PbfRuleForward,
    PbfRuleForwardMonitor,
    PbfRuleForwardNexthop,
    PbfRuleFrom,
    PbfRuleNexthopAddress,
    PbfRuleResponseModel,
    PbfRuleUpdateModel,
)


class TestPbfRuleSubModels:
    """Test PBF Rule sub-model validation."""

    def test_forward_monitor(self):
        """Test PbfRuleForwardMonitor model."""
        model = PbfRuleForwardMonitor(
            profile="monitor-profile",
            disable_if_unreachable=True,
            ip_address="10.0.0.1",
        )
        assert model.profile == "monitor-profile"
        assert model.disable_if_unreachable is True
        assert model.ip_address == "10.0.0.1"

    def test_forward_nexthop_ip(self):
        """Test PbfRuleForwardNexthop with IP address."""
        model = PbfRuleForwardNexthop(ip_address="10.0.0.1")
        assert model.ip_address == "10.0.0.1"
        assert model.fqdn is None

    def test_forward_nexthop_fqdn(self):
        """Test PbfRuleForwardNexthop with FQDN."""
        model = PbfRuleForwardNexthop(fqdn="gateway.example.com")
        assert model.fqdn == "gateway.example.com"
        assert model.ip_address is None

    def test_forward_action(self):
        """Test PbfRuleForward model."""
        model = PbfRuleForward(
            egress_interface="ethernet1/1",
            nexthop=PbfRuleForwardNexthop(ip_address="10.0.0.1"),
            monitor=PbfRuleForwardMonitor(ip_address="10.0.0.2"),
        )
        assert model.egress_interface == "ethernet1/1"
        assert model.nexthop.ip_address == "10.0.0.1"
        assert model.monitor.ip_address == "10.0.0.2"

    def test_action_forward(self):
        """Test PbfRuleAction with forward action."""
        model = PbfRuleAction(
            forward=PbfRuleForward(egress_interface="ethernet1/1"),
        )
        assert model.forward is not None
        assert model.discard is None
        assert model.no_pbf is None

    def test_action_discard(self):
        """Test PbfRuleAction with discard action."""
        model = PbfRuleAction(discard={})
        assert model.discard == {}
        assert model.forward is None
        assert model.no_pbf is None

    def test_action_no_pbf(self):
        """Test PbfRuleAction with no_pbf action."""
        model = PbfRuleAction(no_pbf={})
        assert model.no_pbf == {}
        assert model.forward is None
        assert model.discard is None

    def test_from_zone(self):
        """Test PbfRuleFrom with zone."""
        model = PbfRuleFrom(zone=["trust", "untrust"])
        assert model.zone == ["trust", "untrust"]
        assert model.interface is None

    def test_from_interface(self):
        """Test PbfRuleFrom with interface."""
        model = PbfRuleFrom(interface=["ethernet1/1", "ethernet1/2"])
        assert model.interface == ["ethernet1/1", "ethernet1/2"]
        assert model.zone is None

    def test_nexthop_address(self):
        """Test PbfRuleNexthopAddress model."""
        model = PbfRuleNexthopAddress(name="10.0.0.1")
        assert model.name == "10.0.0.1"

    def test_enforce_symmetric_return(self):
        """Test PbfRuleEnforceSymmetricReturn model."""
        model = PbfRuleEnforceSymmetricReturn(
            enabled=True,
            nexthop_address_list=[
                PbfRuleNexthopAddress(name="10.0.0.1"),
                PbfRuleNexthopAddress(name="10.0.0.2"),
            ],
        )
        assert model.enabled is True
        assert len(model.nexthop_address_list) == 2


class TestPbfRuleBaseModel:
    """Test PBF Rule base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = PbfRuleBaseModel(name="test-rule", folder="Test Folder")
        assert model.name == "test-rule"
        assert model.folder == "Test Folder"
        assert model.description is None
        assert model.tag is None
        assert model.schedule is None
        assert model.disabled is None
        assert model.from_ is None
        assert model.source is None
        assert model.source_user is None
        assert model.destination is None
        assert model.action is None
        assert model.enforce_symmetric_return is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = PbfRuleBaseModel(
            name="test-rule",
            folder="Test Folder",
            description="A test PBF rule",
            tag=["tag1", "tag2"],
            schedule="business-hours",
            disabled=False,
            from_=PbfRuleFrom(zone=["trust"]),
            source=["192.168.1.0/24"],
            source_user=["any"],
            destination=["any"],
            service=["any"],
            application=["any"],
            action=PbfRuleAction(
                forward=PbfRuleForward(egress_interface="ethernet1/1"),
            ),
            enforce_symmetric_return=PbfRuleEnforceSymmetricReturn(enabled=True),
        )
        assert model.name == "test-rule"
        assert model.description == "A test PBF rule"
        assert model.tag == ["tag1", "tag2"]
        assert model.from_.zone == ["trust"]
        assert model.action.forward.egress_interface == "ethernet1/1"

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PbfRuleBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_from_alias(self):
        """Test that from_ field uses alias 'from' in serialization."""
        model = PbfRuleBaseModel(
            name="test-rule",
            folder="Test Folder",
            from_=PbfRuleFrom(zone=["trust"]),
        )
        dumped = model.model_dump(by_alias=True)
        assert "from" in dumped
        assert "from_" not in dumped

    def test_container_folder(self):
        """Test model with folder container."""
        model = PbfRuleBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = PbfRuleBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = PbfRuleBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        # Valid at max length (64 chars)
        model = PbfRuleBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        # Invalid over max length
        with pytest.raises(ValidationError):
            PbfRuleBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        # Valid patterns
        model = PbfRuleBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        # Invalid pattern (special chars)
        with pytest.raises(ValidationError):
            PbfRuleBaseModel(name="test", folder="Folder@#$")


class TestPbfRuleCreateModel:
    """Test PBF Rule create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = PbfRuleCreateModel(
            name="test-rule",
            folder="Test Folder",
        )
        assert model.name == "test-rule"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = PbfRuleCreateModel(
            name="test-rule",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = PbfRuleCreateModel(
            name="test-rule",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            PbfRuleCreateModel(name="test-rule")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            PbfRuleCreateModel(
                name="test-rule",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on PbfRuleCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            PbfRuleCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_create_with_forward_action(self):
        """Test create model with forward action configuration."""
        model = PbfRuleCreateModel(
            name="test-rule",
            folder="Test Folder",
            action=PbfRuleAction(
                forward=PbfRuleForward(
                    egress_interface="ethernet1/1",
                    nexthop=PbfRuleForwardNexthop(ip_address="10.0.0.1"),
                ),
            ),
        )
        assert model.action.forward.egress_interface == "ethernet1/1"
        assert model.action.forward.nexthop.ip_address == "10.0.0.1"

    def test_create_with_discard_action(self):
        """Test create model with discard action."""
        model = PbfRuleCreateModel(
            name="test-rule",
            folder="Test Folder",
            action=PbfRuleAction(discard={}),
        )
        assert model.action.discard == {}

    def test_create_with_no_pbf_action(self):
        """Test create model with no-pbf action."""
        model = PbfRuleCreateModel(
            name="test-rule",
            folder="Test Folder",
            action=PbfRuleAction(no_pbf={}),
        )
        assert model.action.no_pbf == {}

    def test_create_with_from_zone(self):
        """Test create model with from_ field using zone."""
        model = PbfRuleCreateModel(
            name="test-rule",
            folder="Test Folder",
            from_=PbfRuleFrom(zone=["trust"]),
        )
        assert model.from_.zone == ["trust"]


class TestPbfRuleUpdateModel:
    """Test PBF Rule update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = PbfRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-rule",
            folder="Test Folder",
            description="Updated description",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-rule"
        assert model.description == "Updated description"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            PbfRuleUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            PbfRuleUpdateModel(
                name="test",
                folder="Test Folder",
            )


class TestPbfRuleResponseModel:
    """Test PBF Rule response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = PbfRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-rule",
            folder="Test Folder",
            description="A test rule",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-rule"
        assert model.description == "A test rule"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            PbfRuleResponseModel(
                name="test",
                folder="Test Folder",
            )

    def test_response_with_from_alias(self):
        """Test response model from_ field alias handling."""
        model = PbfRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
            folder="Test Folder",
            from_=PbfRuleFrom(zone=["trust"]),
        )
        assert model.from_.zone == ["trust"]
        dumped = model.model_dump(by_alias=True)
        assert "from" in dumped


class TestExtraFieldsPbfRule:
    """Tests for extra field handling on PBF Rule models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on PbfRuleBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            PbfRuleBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on PbfRuleUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            PbfRuleUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on PbfRuleResponseModel."""
        model = PbfRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
