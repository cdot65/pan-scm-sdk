# tests/test_anti_spyware_profiles.py

import pytest
from unittest.mock import MagicMock

from scm.config.security.anti_spyware_profile import AntiSpywareProfile
from scm.exceptions import ValidationError
from scm.models.security.anti_spyware_profiles import (
    AntiSpywareProfileRequestModel,
    AntiSpywareProfileResponseModel,
    Severity,
    Category,
    ActionRequest,
    ActionResponse,
)

from tests.factories import (
    AntiSpywareProfileRequestFactory,
    RuleRequestFactory,
    ThreatExceptionRequestFactory,
)


@pytest.mark.usefixtures("load_env")
class TestAntiSpywareProfileBase:
    """Base class for Anti-Spyware Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AntiSpywareProfile(self.mock_scm)  # noqa


class TestAntiSpywareProfileAPI(TestAntiSpywareProfileBase):
    """Tests for Anti-Spyware Profile API operations."""

    def test_list_anti_spyware_profiles(self):
        """Test listing anti-spyware profiles."""
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "TestProfile1",
                    "folder": "Prisma Access",
                    "description": "A test anti-spyware profile",
                    "rules": [
                        {
                            "name": "TestRule1",
                            "severity": ["critical", "high"],
                            "category": "spyware",
                            "threat_name": "any",
                            "packet_capture": "disable",
                            "action": {"alert": {}},
                        }
                    ],
                    "threat_exception": [
                        {
                            "name": "TestException1",
                            "action": {"allow": {}},
                            "packet_capture": "single-packet",
                            "exempt_ip": [{"name": "192.168.1.1"}],
                            "notes": "Test note",
                        }
                    ],
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440001",
                    "name": "TestProfile2",
                    "folder": "Prisma Access",
                    "rules": [],
                    "threat_exception": [],
                },
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        profiles = self.client.list(folder="Prisma Access")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
            params={"folder": "Prisma Access"},
        )
        assert isinstance(profiles, list)
        assert len(profiles) == 2
        assert isinstance(profiles[0], AntiSpywareProfileResponseModel)
        assert profiles[0].name == "TestProfile1"
        assert profiles[0].description == "A test anti-spyware profile"
        assert profiles[0].rules[0].name == "TestRule1"
        assert profiles[0].rules[0].severity == [Severity.critical, Severity.high]
        assert profiles[0].rules[0].category == Category.spyware
        assert profiles[0].rules[0].action.get_action_name() == "alert"
        assert profiles[0].threat_exception[0].name == "TestException1"
        assert profiles[0].threat_exception[0].action.get_action_name() == "allow"
        assert profiles[0].threat_exception[0].exempt_ip[0].name == "192.168.1.1"

    def test_create_anti_spyware_profile(self):
        """Test creating an anti-spyware profile."""
        test_profile = AntiSpywareProfileRequestFactory()
        mock_response = test_profile.model_dump()
        mock_response["id"] = "333e4567-e89b-12d3-a456-426655440002"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_profile = self.client.create(
            test_profile.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
            json=test_profile.model_dump(exclude_unset=True),
        )
        assert isinstance(created_profile, AntiSpywareProfileResponseModel)
        assert created_profile.id == "333e4567-e89b-12d3-a456-426655440002"
        assert created_profile.name == test_profile.name
        assert created_profile.rules[0].action.get_action_name() == "alert"
        assert created_profile.threat_exception[0].name.startswith("exception_")

    def test_get_anti_spyware_profile(self):
        """Test retrieving an anti-spyware profile by ID."""
        profile_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": profile_id,
            "name": "TestProfile",
            "folder": "Prisma Access",
            "description": "A test anti-spyware profile",
            "rules": [],
            "threat_exception": [],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        profile = self.client.get(profile_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/anti-spyware-profiles/{profile_id}"
        )
        assert isinstance(profile, AntiSpywareProfileResponseModel)
        assert profile.id == profile_id
        assert profile.name == "TestProfile"
        assert profile.description == "A test anti-spyware profile"

    def test_update_anti_spyware_profile(self):
        """Test updating an anti-spyware profile."""
        profile_id = "123e4567-e89b-12d3-a456-426655440000"
        update_data = {
            "name": "UpdatedProfile",
            "folder": "Prisma Access",
            "description": "An updated anti-spyware profile",
            "rules": [
                {
                    "name": "UpdatedRule",
                    "severity": ["high"],
                    "category": "botnet",
                    "packet_capture": "extended-capture",
                    "action": {"block_ip": {"track_by": "source", "duration": 3600}},
                }
            ],
            "threat_exception": [],
        }

        mock_response = update_data.copy()
        mock_response["id"] = profile_id

        self.mock_scm.put.return_value = mock_response  # noqa
        updated_profile = self.client.update(profile_id, update_data)

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/security/v1/anti-spyware-profiles/{profile_id}",
            json=update_data,
        )
        assert isinstance(updated_profile, AntiSpywareProfileResponseModel)
        assert updated_profile.id == profile_id
        assert updated_profile.name == "UpdatedProfile"
        assert updated_profile.description == "An updated anti-spyware profile"
        assert updated_profile.rules[0].action.get_action_name() == "block_ip"

    def test_delete_anti_spyware_profile(self):
        """Test deleting an anti-spyware profile."""
        profile_id = "123e4567-e89b-12d3-a456-426655440000"
        self.client.delete(profile_id)
        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/anti-spyware-profiles/{profile_id}"
        )


class TestAntiSpywareProfileValidation(TestAntiSpywareProfileBase):
    """Tests for Anti-Spyware Profile validation."""

    def test_anti_spyware_profile_list_validation_error(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_anti_spyware_profile_request_model_validation_errors(self):
        """Test validation errors in AntiSpywareProfileRequestModel."""
        # No container provided
        data_no_container = {
            "name": "InvalidProfile",
            "rules": [],
        }
        with pytest.raises(ValueError) as exc_info:
            AntiSpywareProfileRequestModel(**data_no_container)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Multiple containers provided
        data_multiple_containers = {
            "name": "InvalidProfile",
            "folder": "Shared",
            "device": "Device1",
            "rules": [],
        }
        with pytest.raises(ValueError) as exc_info:
            AntiSpywareProfileRequestModel(**data_multiple_containers)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_rule_request_model_validation(self):
        """Test validation in RuleRequest model."""
        # Invalid severity
        with pytest.raises(ValueError) as exc_info:
            RuleRequestFactory(severity=["nonexistent_severity"])
        assert "1 validation error for RuleRequest" in str(exc_info.value)

        # Missing action
        rule = RuleRequestFactory(action=None)
        assert rule.action is None

    def test_threat_exception_request_model_validation(self):
        """Test validation in ThreatExceptionRequest model."""
        # Invalid packet_capture
        with pytest.raises(ValueError) as exc_info:
            ThreatExceptionRequestFactory(packet_capture="invalid_option")
        assert "1 validation error for ThreatExceptionRequest" in str(exc_info.value)

        # Missing action
        with pytest.raises(ValueError) as exc_info:
            ThreatExceptionRequestFactory(action=None)
        assert "1 validation error for ThreatExceptionRequest" in str(exc_info.value)


class TestAntiSpywareProfilePagination(TestAntiSpywareProfileBase):
    """Tests for Anti-Spyware Profile pagination functionality."""

    def test_list_anti_spyware_profiles_with_pagination(self):
        """Test listing anti-spyware profiles with pagination parameters."""
        mock_response = {
            "data": [
                {
                    "id": "223e4567-e89b-12d3-a456-426655440001",
                    "name": "TestProfile2",
                    "folder": "Prisma Access",
                    "rules": [],
                    "threat_exception": [],
                },
            ],
            "offset": 1,
            "total": 2,
            "limit": 1,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        profiles = self.client.list(folder="Prisma Access", offset=1, limit=1)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
            params={"folder": "Prisma Access", "offset": 1, "limit": 1},
        )
        assert isinstance(profiles, list)
        assert len(profiles) == 1
        assert profiles[0].name == "TestProfile2"
        assert profiles[0].id == "223e4567-e89b-12d3-a456-426655440001"

    def test_list_anti_spyware_profiles_with_invalid_pagination(self):
        """Test validation error when invalid pagination parameters are provided."""
        with pytest.raises(ValueError) as exc_info:
            self.client.list(
                folder="Prisma Access",
                offset=-1,
                limit=0,
            )
        assert "Offset must be a non-negative integer" in str(exc_info.value)
        assert "Limit must be a positive integer" in str(exc_info.value)


class TestAntiSpywareProfileFilters(TestAntiSpywareProfileBase):
    """Tests for Anti-Spyware Profile filtering functionality."""

    def test_list_anti_spyware_profiles_with_name_filter(self):
        """Test listing anti-spyware profiles with name filter."""
        mock_response = {
            "data": [
                {
                    "id": "223e4567-e89b-12d3-a456-426655440001",
                    "name": "SpecificProfile",
                    "folder": "Prisma Access",
                    "rules": [],
                    "threat_exception": [],
                },
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        profiles = self.client.list(folder="Prisma Access", name="SpecificProfile")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
            params={"folder": "Prisma Access", "name": "SpecificProfile"},
        )
        assert isinstance(profiles, list)
        assert len(profiles) == 1
        assert profiles[0].name == "SpecificProfile"

    def test_list_anti_spyware_profiles_with_all_parameters(self):
        """Test listing anti-spyware profiles with all optional parameters."""
        mock_response = {
            "data": [],
            "offset": 10,
            "total": 2,
            "limit": 5,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        profiles = self.client.list(
            folder="Prisma Access",
            name="TestProfile",
            offset=10,
            limit=5,
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
            params={
                "folder": "Prisma Access",
                "name": "TestProfile",
                "offset": 10,
                "limit": 5,
            },
        )
        assert isinstance(profiles, list)
        assert len(profiles) == 0


class TestAntiSpywareProfileActions(TestAntiSpywareProfileBase):
    """Tests for Anti-Spyware Profile action functionality."""

    def test_action_request_check_and_transform_action(self):
        """Test action request validation and transformation."""
        # Test string input
        action = ActionRequest("alert")  # noqa
        assert action.root == {"alert": {}}

        # Test dict input
        action = ActionRequest({"drop": {}})
        assert action.root == {"drop": {}}

        # Test invalid input type
        with pytest.raises(
            ValueError, match="Invalid action format; must be a string or dict."
        ):
            ActionRequest(123)  # noqa

        # Test multiple actions
        with pytest.raises(
            ValueError, match="Exactly one action must be provided in 'action' field."
        ):
            ActionRequest({"alert": {}, "drop": {}})

        # Test empty dict
        with pytest.raises(
            ValueError, match="Exactly one action must be provided in 'action' field."
        ):
            ActionRequest({})

    def test_action_request_get_action_name(self):
        """Test getting action names from requests."""
        action = ActionRequest("alert")  # noqa
        assert action.get_action_name() == "alert"

        action = ActionRequest({"drop": {}})
        assert action.get_action_name() == "drop"

    def test_action_response_check_action(self):
        """Test action response validation."""
        # Test string input
        action = ActionResponse("alert")  # noqa
        assert action.root == {"alert": {}}

        # Test dict input
        action = ActionResponse({"drop": {}})
        assert action.root == {"drop": {}}

        # Test invalid input type
        with pytest.raises(
            ValueError, match="Invalid action format; must be a string or dict."
        ):
            ActionResponse(123)  # noqa

        # Test multiple actions
        with pytest.raises(
            ValueError, match="At most one action must be provided in 'action' field."
        ):
            ActionResponse({"alert": {}, "drop": {}})

        # Test empty dict (should be allowed for ActionResponse)
        action = ActionResponse({})
        assert action.root == {}

    def test_action_response_get_action_name(self):
        """Test getting action names from responses."""
        action = ActionResponse("alert")  # noqa
        assert action.get_action_name() == "alert"

        action = ActionResponse({"drop": {}})
        assert action.get_action_name() == "drop"

        action = ActionResponse({})
        assert action.get_action_name() == "unknown"

    def test_anti_spyware_profile_response_model_invalid_uuid(self):
        """Test UUID validation in AntiSpywareProfileResponseModel."""
        # Test invalid UUID format
        invalid_data = {
            "id": "invalid-uuid-format",
            "name": "TestProfile",
            "folder": "Prisma Access",
            "rules": [],
            "threat_exception": [],
        }
        with pytest.raises(ValueError) as exc_info:
            AntiSpywareProfileResponseModel(**invalid_data)
        assert "Invalid UUID format for 'id'" in str(exc_info.value)

        # Test valid UUID format
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Prisma Access",
            "rules": [],
            "threat_exception": [],
        }
        profile = AntiSpywareProfileResponseModel(**valid_data)
        assert profile.id == "123e4567-e89b-12d3-a456-426655440000"

        # Test completely malformed UUID
        malformed_data = {
            "id": "123",
            "name": "TestProfile",
            "folder": "Prisma Access",
            "rules": [],
            "threat_exception": [],
        }
        with pytest.raises(ValueError) as exc_info:
            AntiSpywareProfileResponseModel(**malformed_data)
        assert "Invalid UUID format for 'id'" in str(exc_info.value)


class TestSuite(
    TestAntiSpywareProfileAPI,
    TestAntiSpywareProfileValidation,
    TestAntiSpywareProfilePagination,
    TestAntiSpywareProfileFilters,
    TestAntiSpywareProfileActions,
):
    """Main test suite that combines all test classes."""

    pass
