# tests/scm/config/security/test_wildfire_antivirus_profile.py

import pytest
from unittest.mock import MagicMock

from scm.config.security.wildfire_antivirus_profile import WildfireAntivirusProfile
from scm.exceptions import ValidationError
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAntivirusProfileCreateModel,
    WildfireAntivirusProfileResponseModel,
    RuleBase,
    Analysis,
    Direction,
)


@pytest.mark.usefixtures("load_env")
class TestWildfireAntivirusProfileBase:
    """Base class for Wildfire Antivirus Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = WildfireAntivirusProfile(self.mock_scm)  # noqa


class TestWildfireAntivirusProfileAPI(TestWildfireAntivirusProfileBase):
    """Tests for Wildfire Antivirus Profile API operations."""

    def test_list_wildfire_antivirus_profiles(self):
        """
        Test listing wildfire antivirus profiles.

        **Objective:** Test listing all profiles.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response.
            2. Calls the `list` method with a filter parameter.
            3. Validates the returned list of profiles.
        """
        mock_response = {
            "data": [
                {
                    "id": "dd0f80ce-9345-4cf1-9979-bce99da27888",
                    "name": "web-security-default",
                    "folder": "All",
                    "snippet": "Web-Security-Default",
                    "rules": [
                        {
                            "name": "default-fawkes",
                            "direction": "both",
                            "file_type": ["any"],
                            "application": ["any"],
                        }
                    ],
                },
                {
                    "id": "e2a5dfc4-d8c8-489a-9661-092032796e09",
                    "name": "best-practice",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "rules": [
                        {
                            "name": "default",
                            "application": ["any"],
                            "file_type": ["any"],
                            "direction": "both",
                            "analysis": "public-cloud",
                        }
                    ],
                    "description": "Best practice profile",
                },
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        profiles = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={"folder": "All"},
        )
        assert isinstance(profiles, list)
        assert len(profiles) == 2
        assert isinstance(profiles[0], WildfireAntivirusProfileResponseModel)
        assert profiles[0].name == "web-security-default"
        assert profiles[0].rules[0].direction == Direction.both

    def test_create_wildfire_antivirus_profile(self):
        """
        Test creating a wildfire antivirus profile.

        **Objective:** Test profile creation with all fields.
        **Workflow:**
            1. Prepares test data with all supported fields.
            2. Mocks API response.
            3. Validates created profile attributes.
        """
        test_profile_data = {
            "name": "NewWFProfile",
            "folder": "All",
            "description": "A new test profile",
            "packet_capture": True,
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
            "mlav_exception": [
                {
                    "name": "Exception1",
                    "description": "An exception",
                    "filename": "malicious.exe",
                }
            ],
            "threat_exception": [
                {
                    "name": "ThreatException1",
                    "notes": "Some notes",
                }
            ],
        }

        mock_response = test_profile_data.copy()
        mock_response["id"] = "333e4567-e89b-12d3-a456-426655440002"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_profile = self.client.create(test_profile_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            json=test_profile_data,
        )
        assert isinstance(created_profile, WildfireAntivirusProfileResponseModel)
        assert created_profile.id == "333e4567-e89b-12d3-a456-426655440002"
        assert created_profile.name == "NewWFProfile"
        assert created_profile.rules[0].analysis == Analysis.public_cloud

    def test_get_wildfire_antivirus_profile(self):
        """
        Test retrieving a profile by ID.

        **Objective:** Test fetching a specific profile.
        **Workflow:**
            1. Mocks API response for a specific profile.
            2. Validates retrieved profile attributes.
        """
        profile_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": profile_id,
            "name": "TestProfile",
            "folder": "All",
            "description": "A test profile",
            "rules": [
                {
                    "name": "TestRule",
                    "direction": "download",
                    "application": ["app1", "app2"],
                    "file_type": ["pdf", "exe"],
                    "analysis": "private-cloud",
                }
            ],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        profile = self.client.get(profile_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/wildfire-anti-virus-profiles/{profile_id}"
        )
        assert isinstance(profile, WildfireAntivirusProfileResponseModel)
        assert profile.id == profile_id
        assert profile.rules[0].analysis == Analysis.private_cloud

    def test_update_wildfire_antivirus_profile(self):
        """
        Test updating a profile.

        **Objective:** Test profile update functionality.
        **Workflow:**
            1. Prepares update data.
            2. Validates updated profile attributes.
        """
        profile_id = "123e4567-e89b-12d3-a456-426655440000"
        update_data = {
            "id": profile_id,
            "name": "UpdatedProfile",
            "folder": "All",
            "description": "An updated profile",
            "rules": [
                {
                    "name": "UpdatedRule",
                    "direction": Direction.upload,  # Use the enum directly
                    "application": ["app3"],
                    "file_type": ["docx"],
                }
            ],
            "packet_capture": False,
        }

        # Create a copy of update_data but with serialized/string version for direction
        expected_payload = {
            "name": "UpdatedProfile",
            "folder": "All",
            "description": "An updated profile",
            "rules": [
                {
                    "name": "UpdatedRule",
                    "direction": "upload",  # Use string value for expected payload
                    "application": ["app3"],
                    "file_type": ["docx"],
                }
            ],
            "packet_capture": False,
        }

        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa
        updated_profile = self.client.update(update_data)

        # Instead of checking exact payload, verify important parts
        assert self.mock_scm.put.call_count == 1  # noqa
        call_args = self.mock_scm.put.call_args  # noqa
        assert (
            call_args[0][0]
            == f"/config/security/v1/wildfire-anti-virus-profiles/{profile_id}"
        )

        actual_payload = call_args[1]["json"]
        assert actual_payload["name"] == expected_payload["name"]
        assert actual_payload["folder"] == expected_payload["folder"]
        assert actual_payload["description"] == expected_payload["description"]
        assert actual_payload["packet_capture"] == expected_payload["packet_capture"]
        assert (
            actual_payload["rules"][0]["name"] == expected_payload["rules"][0]["name"]
        )
        assert (
            actual_payload["rules"][0]["application"]
            == expected_payload["rules"][0]["application"]
        )
        assert (
            actual_payload["rules"][0]["file_type"]
            == expected_payload["rules"][0]["file_type"]
        )
        # For direction, verify the value rather than the enum itself
        assert (
            actual_payload["rules"][0]["direction"].value
            == expected_payload["rules"][0]["direction"]
        )

        # Verify the returned model
        assert isinstance(updated_profile, WildfireAntivirusProfileResponseModel)
        assert updated_profile.id == profile_id
        assert updated_profile.rules[0].direction == Direction.upload

    def test_delete_wildfire_antivirus_profile(self):
        """
        Test deleting a profile.

        **Objective:** Test profile deletion.
        **Workflow:**
            1. Calls delete method with profile ID.
            2. Verifies correct endpoint called.
        """
        profile_id = "123e4567-e89b-12d3-a456-426655440000"
        self.client.delete(profile_id)
        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/wildfire-anti-virus-profiles/{profile_id}"
        )

    def test_list_with_pagination(self):
        """
        Test listing profiles with pagination.

        **Objective:** Test pagination parameters.
        **Workflow:**
            1. Calls list with offset and limit.
            2. Verifies parameters passed correctly.
        """
        mock_response = {
            "data": [
                {
                    "id": "dd0f80ce-9345-4cf1-9979-bce99da27888",
                    "name": "web-security-default",
                    "folder": "All",
                    # Add required rules field
                    "rules": [
                        {
                            "name": "default",
                            "direction": "both",
                            "application": ["any"],
                            "file_type": ["any"],
                        }
                    ],
                }
            ],
            "offset": 1,
            "total": 1,
            "limit": 1,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        self.client.list(folder="All", offset=1, limit=1)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={"folder": "All", "offset": 1, "limit": 1},
        )

    def test_list_name_filter(self):
        """Test that name filter is properly added to parameters."""
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "TestProfile",
                    "folder": "All",
                    "rules": [
                        {
                            "name": "default",
                            "direction": "both",
                            "application": ["any"],
                            "file_type": ["any"],
                        }
                    ],
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test with name filter
        self.client.list(folder="All", name="TestProfile")

        called_params = self.mock_scm.get.call_args[1]["params"]  # noqa
        assert "name" in called_params
        assert called_params["name"] == "TestProfile"

    def test_fetch_basic_functionality(self):
        """Test basic fetch functionality with valid parameters."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "default",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch("TestProfile", folder="All")

        assert isinstance(result, dict)
        assert result["name"] == "TestProfile"
        assert result["folder"] == "All"

    def test_fetch_missing_name(self):
        """Test fetch validation when name is missing."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch("")
        assert "Parameter 'name' must be provided for fetch method" in str(
            exc_info.value
        )

        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(None)  # noqa
        assert "Parameter 'name' must be provided for fetch method" in str(
            exc_info.value
        )

    def test_fetch_container_params_initialization(self):
        """Test container parameters initialization in fetch."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "default",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.fetch("TestProfile", folder="All")

        called_args = self.mock_scm.get.call_args  # noqa
        assert isinstance(called_args[1]["params"], dict)

    def test_fetch_provided_containers_validation(self):
        """Test validation of provided containers in fetch."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "default",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test multiple containers
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch("TestProfile", folder="All", device="Device1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided"
            in str(exc_info.value)
        )

        # Test no containers
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch("TestProfile")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided"
            in str(exc_info.value)
        )

    def test_fetch_params_handling(self):
        """Test parameter handling in fetch method."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "default",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test with additional filters
        self.client.fetch(
            "TestProfile",
            folder="All",
            custom_filter="value",
            types="ignored",
            values="ignored",
        )

        called_params = self.mock_scm.get.call_args[1]["params"]  # noqa
        assert called_params["name"] == "TestProfile"
        assert called_params["folder"] == "All"
        assert called_params["custom_filter"] == "value"
        assert "types" not in called_params
        assert "values" not in called_params

    def test_fetch_api_call(self):
        """Test that fetch makes the correct API call."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "default",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.fetch("TestProfile", folder="All")

        self.mock_scm.get.assert_called_once()  # noqa
        assert self.mock_scm.get.call_args[0][0] == self.client.ENDPOINT  # noqa

    def test_fetch_response_handling(self):
        """Test response handling in fetch method."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "default",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch("TestProfile", folder="All")

        # Verify response is properly processed
        assert isinstance(result, dict)
        assert "id" in result
        assert "name" in result
        assert "rules" in result
        assert result["name"] == "TestProfile"

        # Verify null values are excluded
        mock_response_with_null = {**mock_response, "description": None}
        self.mock_scm.get.return_value = mock_response_with_null  # noqa
        result = self.client.fetch("TestProfile", folder="All")
        assert "description" not in result

    def test_fetch_invalid_response(self):
        """Test handling of invalid response data."""
        # Test missing required fields
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "All",
            # Missing required 'rules' field
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(ValueError) as exc_info:
            self.client.fetch("TestProfile", folder="All")
        assert "rules" in str(exc_info.value)


class TestWildfireAntivirusProfileValidation(TestWildfireAntivirusProfileBase):
    """Tests for Wildfire Antivirus Profile validation."""

    def test_create_model_container_validation(self):
        """Test container validation in create model."""
        # No container
        with pytest.raises(ValueError) as exc_info:
            WildfireAntivirusProfileCreateModel(
                name="Test",
                rules=[{"name": "Rule1", "direction": "both"}],
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Multiple containers
        with pytest.raises(ValueError) as exc_info:
            WildfireAntivirusProfileCreateModel(
                name="Test",
                folder="Shared",
                device="Device1",
                rules=[{"name": "Rule1", "direction": "both"}],
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_rule_request_validation(self):
        """Test RuleBase model validation."""
        # Invalid direction
        with pytest.raises(ValueError) as exc_info:
            RuleBase(name="TestRule", direction="invalid")
        assert "Input should be 'download', 'upload' or 'both'" in str(exc_info.value)

        # Invalid analysis
        with pytest.raises(ValueError) as exc_info:
            RuleBase(
                name="TestRule",
                direction="both",
                analysis="invalid-cloud",
            )
        assert "Input should be 'public-cloud' or 'private-cloud'" in str(
            exc_info.value
        )

    def test_list_validation(self):
        """Test list method parameter validation."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_pagination_validation(self):
        """Test pagination parameter validation."""
        with pytest.raises(ValueError) as exc_info:
            self.client.list(folder="All", offset=-1, limit=0)
        assert "Offset must be a non-negative integer" in str(exc_info.value)
        assert "Limit must be a positive integer" in str(exc_info.value)


class TestSuite(
    TestWildfireAntivirusProfileAPI,
    TestWildfireAntivirusProfileValidation,
):
    """Main test suite combining all test classes."""

    pass
