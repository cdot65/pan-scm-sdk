# tests/scm/models/security/test_anti_spyware_profile_models.py

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.security.anti_spyware_profiles import (
    AntiSpywareProfileCreateModel,
    AntiSpywareProfileUpdateModel,
    AntiSpywareProfileResponseModel,
    RuleBaseModel,
    ThreatExceptionBase,
    ActionRequest,
    ActionResponse,
    BlockIpAction,
    Category,
    Severity,
    PacketCapture,
    ExemptIpEntry,
)
from tests.factories import (
    AntiSpywareProfileCreateModelFactory,
    AntiSpywareProfileUpdateModelFactory,
)


# -------------------- Test Classes for Pydantic Models --------------------


class TestRuleBaseModel:
    """Tests for RuleBaseModel validation."""

    def test_rule_base_model_valid(self):
        """Test validation with valid data."""
        data = {
            "name": "TestRule",
            "severity": [Severity.critical, Severity.high],
            "category": Category.spyware,
            "threat_name": "test_threat",
            "packet_capture": PacketCapture.disable,
        }
        model = RuleBaseModel(**data)
        assert model.name == data["name"]
        assert model.severity == data["severity"]
        assert model.category == data["category"]
        assert model.threat_name == data["threat_name"]
        assert model.packet_capture == data["packet_capture"]

    def test_rule_base_model_invalid_severity(self):
        """Test validation with invalid severity."""
        data = {
            "name": "TestRule",
            "severity": ["invalid"],
            "category": Category.spyware,
        }
        with pytest.raises(ValidationError) as exc_info:
            RuleBaseModel(**data)
        assert "Input should be 'critical'" in str(exc_info.value)

    def test_rule_base_model_invalid_category(self):
        """Test validation with invalid category."""
        data = {
            "name": "TestRule",
            "severity": [Severity.critical],
            "category": "invalid",
        }
        with pytest.raises(ValidationError) as exc_info:
            RuleBaseModel(**data)
        assert "Input should be 'dns-proxy'" in str(exc_info.value)


class TestThreatExceptionBase:
    """Tests for ThreatExceptionBase validation."""

    def test_threat_exception_base_valid(self):
        """Test validation with valid data."""
        data = {
            "name": "TestException",
            "packet_capture": PacketCapture.single_packet,
            "exempt_ip": [{"name": "192.168.1.1"}],
            "notes": "Test notes",
        }
        model = ThreatExceptionBase(**data)
        assert model.name == data["name"]
        assert model.packet_capture == data["packet_capture"]
        assert isinstance(model.exempt_ip[0], ExemptIpEntry)
        assert model.notes == data["notes"]

    def test_threat_exception_base_invalid_packet_capture(self):
        """Test validation with invalid packet capture."""
        data = {
            "name": "TestException",
            "packet_capture": "invalid",
        }
        with pytest.raises(ValidationError) as exc_info:
            ThreatExceptionBase(**data)
        assert "Input should be 'disable'" in str(exc_info.value)


class TestAntiSpywareProfileCreateModel:
    """Tests for AntiSpywareProfileCreateModel validation."""

    def test_profile_create_model_valid(self):
        """Test validation with valid data."""
        data = AntiSpywareProfileCreateModelFactory.build_valid()
        model = AntiSpywareProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert len(model.rules) > 0
        assert isinstance(model.rules[0], RuleBaseModel)

    def test_profile_create_model_invalid_name(self):
        """Test validation with invalid name pattern."""
        data = AntiSpywareProfileCreateModelFactory.build_valid()
        data["name"] = "@invalid_name"
        with pytest.raises(ValidationError) as exc_info:
            AntiSpywareProfileCreateModel(**data)
        assert "String should match pattern" in str(exc_info.value)

    def test_profile_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = AntiSpywareProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            AntiSpywareProfileCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )


class TestAntiSpywareProfileUpdateModel:
    """Tests for AntiSpywareProfileUpdateModel validation."""

    def test_profile_update_model_valid(self):
        """Test validation with valid update data."""
        data = AntiSpywareProfileUpdateModelFactory.build_valid()
        model = AntiSpywareProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert model.description == data["description"]
        assert isinstance(model.rules[0], RuleBaseModel)

    def test_profile_update_model_partial_update(self):
        """Test validation with partial update data."""
        data = {
            "name": "UpdatedProfile",
            "description": "Updated description",
            "rules": [],
        }
        model = AntiSpywareProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert model.description == data["description"]
        assert len(model.rules) == 0


class TestAntiSpywareProfileResponseModel:
    """Tests for AntiSpywareProfileResponseModel validation."""

    def test_profile_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Shared",
            "rules": [
                {
                    "name": "TestRule",
                    "severity": [Severity.critical],
                    "category": Category.spyware,
                }
            ],
        }
        model = AntiSpywareProfileResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert isinstance(model.rules[0], RuleBaseModel)

    def test_profile_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestProfile",
            "folder": "Shared",
            "rules": [],
        }
        with pytest.raises(ValidationError) as exc_info:
            AntiSpywareProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)


class TestActionModels:
    """Tests for Action-related models validation."""

    def test_action_request_valid(self):
        """Test validation of ActionRequest with valid data."""
        data = {"alert": {}}
        model = ActionRequest.model_validate(data)
        assert model.get_action_name() == "alert"

    def test_action_request_with_block_ip(self):
        """Test validation of ActionRequest with block_ip action."""
        data = {
            "block_ip": {
                "track_by": "source",
                "duration": 3600,
            }
        }
        model = ActionRequest.model_validate(data)
        assert model.get_action_name() == "block_ip"

    def test_action_response_empty(self):
        """Test validation of empty ActionResponse."""
        data = {}
        model = ActionResponse.model_validate(data)
        assert model.get_action_name() == "unknown"

    def test_block_ip_action_valid(self):
        """Test validation of BlockIpAction."""
        data = {
            "track_by": "source",
            "duration": 3600,
        }
        model = BlockIpAction(**data)
        assert model.track_by == data["track_by"]
        assert model.duration == data["duration"]

    def test_block_ip_action_invalid_duration(self):
        """Test validation of BlockIpAction with invalid duration."""
        data = {
            "track_by": "source",
            "duration": 3601,  # Exceeds maximum
        }
        with pytest.raises(ValidationError) as exc_info:
            BlockIpAction(**data)
        assert "Input should be less than or equal to 3600" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
