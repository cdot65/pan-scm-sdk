# tests/scm/models/security/test_dns_security_profiles.py

from uuid import UUID

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.security.dns_security_profiles import (
    ActionEnum,
    DNSSecurityProfileCreateModel,
    DNSSecurityProfileResponseModel,
    DNSSecurityProfileUpdateModel,
    ListActionBaseModel,
    ListActionRequestModel,
)
from tests.factories import (
    DNSSecurityProfileCreateApiFactory,
    DNSSecurityProfileCreateModelFactory,
    DNSSecurityProfileResponseFactory,
    DNSSecurityProfileUpdateApiFactory,
    DNSSecurityProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestListActionBaseModel:
    """Tests for ListActionBaseModel."""

    def test_get_action_name_with_valid_dict(self):
        """Test get_action_name returns correct action from dict."""
        model = ListActionBaseModel.model_validate({"block": {}})
        assert model.get_action_name() == "block"

    def test_get_action_name_with_empty_dict(self):
        """Test get_action_name returns 'unknown' for empty dict."""
        model = ListActionBaseModel.model_validate({})
        assert model.get_action_name() == "unknown"

    def test_get_action_name_with_multiple_actions(self):
        """Test get_action_name returns first action when multiple are present."""
        model = ListActionBaseModel.model_validate({"allow": {}, "block": {}})
        assert model.get_action_name() == "allow"


class TestListActionRequestModel:
    """Tests for ListActionRequestModel validation."""

    def test_valid_string_action(self):
        """Test validation with valid string action."""
        model = ListActionRequestModel.model_validate("block")
        assert model.root == {"block": {}}
        assert model.get_action_name() == "block"

    def test_valid_dict_action(self):
        """Test validation with valid dict action."""
        model = ListActionRequestModel.model_validate({"allow": {}})
        assert model.root == {"allow": {}}
        assert model.get_action_name() == "allow"

    def test_invalid_action_type(self):
        """Test validation with invalid action type."""
        with pytest.raises(ValueError) as exc_info:
            ListActionRequestModel.model_validate(["block"])
        assert "Invalid action format; must be a string or dict." in str(exc_info.value)

    def test_no_action_provided(self):
        """Test validation when no action is provided."""
        with pytest.raises(ValueError) as exc_info:
            ListActionRequestModel.model_validate({})
        assert "Exactly one action must be provided in 'action' field." in str(exc_info.value)

    def test_multiple_actions_provided(self):
        """Test validation when multiple actions are provided."""
        with pytest.raises(ValueError) as exc_info:
            ListActionRequestModel.model_validate({"block": {}, "allow": {}})
        assert "Exactly one action must be provided in 'action' field." in str(exc_info.value)

    def test_invalid_action_name(self):
        """Test validation with invalid action name."""
        with pytest.raises(ValueError) as exc_info:
            ListActionRequestModel.model_validate({"invalid_action": {}})
        assert "Exactly one action must be provided in 'action' field." in str(exc_info.value)

    def test_action_with_parameters(self):
        """Test validation when action contains parameters."""
        with pytest.raises(ValueError) as exc_info:
            ListActionRequestModel.model_validate({"block": {"param": "value"}})
        assert "Action 'block' does not take any parameters." in str(exc_info.value)

    @pytest.mark.parametrize(
        "action",
        ["alert", "allow", "block", "sinkhole"],
    )
    def test_all_valid_actions(self, action):
        """Test validation with all possible valid actions."""
        model = ListActionRequestModel.model_validate(action)
        assert model.root == {action: {}}
        assert model.get_action_name() == action

    def test_none_value(self):
        """Test validation with None value."""
        with pytest.raises(ValueError) as exc_info:
            ListActionRequestModel.model_validate(None)
        assert "Invalid action format; must be a string or dict." in str(exc_info.value)

    def test_empty_string(self):
        """Test validation with empty string."""
        with pytest.raises(ValueError) as exc_info:
            ListActionRequestModel.model_validate("")
        assert "Exactly one action must be provided in 'action' field." in str(exc_info.value)


class TestDNSSecurityProfileCreateModel:
    """Tests for DNS Security Profile Create model validation."""

    def test_dns_security_profile_create_model_valid(self):
        """Test validation with valid data."""
        data = DNSSecurityProfileCreateModelFactory.build_valid()
        model = DNSSecurityProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert len(model.botnet_domains.dns_security_categories) == 1
        assert model.botnet_domains.dns_security_categories[0].action == ActionEnum.block

    def test_dns_security_profile_create_model_invalid_name(self):
        """Test validation when an invalid name is provided."""
        data = DNSSecurityProfileCreateModelFactory.build_with_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            DNSSecurityProfileCreateModel(**data)
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_dns_security_profile_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = DNSSecurityProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            DNSSecurityProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_dns_security_profile_create_model_invalid_action(self):
        """Test validation when invalid action is provided in botnet domains."""
        data = DNSSecurityProfileCreateModelFactory.build_with_invalid_action()
        with pytest.raises(ValidationError) as exc_info:
            DNSSecurityProfileCreateModel(**data)
        assert "action\n  Input should be 'default', 'allow', 'block' or 'sinkhole'" in str(
            exc_info.value
        )

    def test_dns_security_profile_create_model_with_snippet(self):
        """Test creation with snippet container."""
        model = DNSSecurityProfileCreateApiFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_dns_security_profile_create_model_with_device(self):
        """Test creation with device container."""
        model = DNSSecurityProfileCreateApiFactory.with_device()
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_dns_security_profile_create_model_empty_botnet_domains(self):
        """Test creation with empty botnet domains configuration."""
        model = DNSSecurityProfileCreateApiFactory.with_empty_botnet_domains()
        assert len(model.botnet_domains.dns_security_categories) == 0
        assert len(model.botnet_domains.lists) == 0
        assert len(model.botnet_domains.whitelist) == 0


class TestDNSSecurityProfileUpdateModel:
    """Tests for DNS Security Profile Update model validation."""

    def test_dns_security_profile_update_model_valid(self):
        """Test validation with valid update data."""
        data = DNSSecurityProfileUpdateModelFactory.build_valid()
        model = DNSSecurityProfileUpdateModel(**data)
        assert model.name == "UpdatedProfile"
        assert model.description == "Updated description"
        assert model.botnet_domains.sinkhole is not None

    def test_dns_security_profile_update_model_invalid_fields(self):
        """Test validation with multiple invalid fields."""
        data = DNSSecurityProfileUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            DNSSecurityProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "name\n  String should match pattern" in error_msg
        assert "action\n  Input should be" in error_msg

    def test_dns_security_profile_update_model_minimal_update(self):
        """Test validation with minimal valid update fields."""
        data = DNSSecurityProfileUpdateModelFactory.build_minimal_update()
        model = DNSSecurityProfileUpdateModel(**data)
        assert model.description == "Updated description"

    def test_dns_security_profile_update_model_with_updated_sinkhole(self):
        """Test update with modified sinkhole settings."""
        model = DNSSecurityProfileUpdateApiFactory.with_updated_sinkhole()
        assert model.botnet_domains.sinkhole.ipv4_address == "127.0.0.1"
        assert model.botnet_domains.sinkhole.ipv6_address == "::1"


class TestDNSSecurityProfileResponseModel:
    """Tests for DNS Security Profile Response model validation."""

    def test_dns_security_profile_response_model_valid(self):
        """Test validation with valid response data."""
        data = DNSSecurityProfileResponseFactory().model_dump()
        model = DNSSecurityProfileResponseModel(**data)
        assert isinstance(model.id, UUID)
        assert model.name.startswith("dns_security_profile_")
        assert model.folder == "Texas"
        assert model.botnet_domains is not None

    def test_dns_security_profile_response_model_from_request(self):
        """Test creation of response model from request data."""
        request_data = DNSSecurityProfileCreateModelFactory.build_valid()
        request_model = DNSSecurityProfileCreateModel(**request_data)
        response_data = DNSSecurityProfileResponseFactory.from_request(request_model)
        model = DNSSecurityProfileResponseModel(**response_data.model_dump())
        assert isinstance(model.id, UUID)
        assert model.name == request_model.name
        assert model.folder == request_model.folder

    def test_dns_security_profile_response_model_with_snippet(self):
        """Test response model with snippet container."""
        data = DNSSecurityProfileResponseFactory.with_snippet()
        model = DNSSecurityProfileResponseModel(**data.model_dump())
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_dns_security_profile_response_model_with_device(self):
        """Test response model with device container."""
        data = DNSSecurityProfileResponseFactory.with_device()
        model = DNSSecurityProfileResponseModel(**data.model_dump())
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None


# -------------------- End of Test Classes --------------------
