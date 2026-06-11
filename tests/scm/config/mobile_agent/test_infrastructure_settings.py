"""Test module for Mobile Agent Infrastructure Settings configuration service.

This module contains unit tests for the Mobile Agent Infrastructure Settings configuration service and its related models.
"""
# tests/scm/config/mobile_agent/test_infrastructure_settings.py

from unittest.mock import MagicMock, patch

import pytest

from scm.config.mobile_agent import InfrastructureSettings
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import InfrastructureSettingsResponseModel

TEST_ID = "123e4567-e89b-12d3-a456-426655440000"


def build_settings_dict(name: str = "test-infra-settings", with_id: bool = True) -> dict:
    """Build a valid infrastructure settings dictionary for tests."""
    data = {
        "name": name,
        "dns_servers": [
            {
                "name": "dns-config",
                "dns_suffix": ["example.com"],
                "primary_public_dns": {"dns_server": "8.8.8.8"},
                "secondary_public_dns": {"dns_server": "8.8.4.4"},
            }
        ],
        "ip_pools": [
            {
                "name": "ip-pool-1",
                "ip_pool": ["10.10.0.0/16"],
            }
        ],
        "portal_hostname": {
            "default_domain": {"hostname": "acme"},
        },
    }
    if with_id:
        data["id"] = TEST_ID
    return data


class TestInfrastructureSettings:
    """Test cases for InfrastructureSettings mobile agent configuration."""

    @pytest.fixture
    def mock_api_client(self):
        """Test fixture for mock API client."""
        mock_client = MagicMock()
        return mock_client

    @pytest.fixture
    def infrastructure_settings(self, mock_api_client):
        """Test fixture for InfrastructureSettings instance."""
        # Patch the isinstance check
        with patch("scm.config.isinstance", return_value=True):
            service = InfrastructureSettings(mock_api_client)
            service.logger = MagicMock()
            return service

    def test_init_with_default_max_limit(self, mock_api_client):
        """Test initialization with default max limit value."""
        with patch("scm.config.isinstance", return_value=True):
            service = InfrastructureSettings(mock_api_client)
            assert service._max_limit == InfrastructureSettings.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_api_client):
        """Test initialization with custom max limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 1000
            service = InfrastructureSettings(mock_api_client, max_limit=custom_limit)
            assert service._max_limit == custom_limit

    def test_validate_max_limit_with_invalid_type(self, infrastructure_settings):
        """Test validate_max_limit with invalid type."""
        with pytest.raises(InvalidObjectError) as excinfo:
            infrastructure_settings._validate_max_limit("not_an_int")
        error = excinfo.value
        assert "Invalid max_limit type" in str(error.details)

    def test_validate_max_limit_with_negative_value(self, infrastructure_settings):
        """Test validate_max_limit with negative value."""
        with pytest.raises(InvalidObjectError) as excinfo:
            infrastructure_settings._validate_max_limit(-1)
        error = excinfo.value
        assert "Invalid max_limit value" in str(error.details)

    def test_validate_max_limit_with_too_large_value(self, infrastructure_settings):
        """Test validate_max_limit with value exceeding absolute max."""
        with pytest.raises(InvalidObjectError) as excinfo:
            infrastructure_settings._validate_max_limit(
                InfrastructureSettings.ABSOLUTE_MAX_LIMIT + 1
            )
        error = excinfo.value
        assert "max_limit exceeds maximum allowed value" in str(error.details)

    def test_validate_max_limit_with_valid_value(self, infrastructure_settings):
        """Test validate_max_limit with valid value."""
        result = infrastructure_settings._validate_max_limit(1000)
        assert result == 1000

    def test_max_limit_property_getter(self, infrastructure_settings):
        """Test max_limit property getter."""
        infrastructure_settings._max_limit = 1000
        assert infrastructure_settings.max_limit == 1000

    def test_max_limit_property_setter(self, infrastructure_settings):
        """Test max_limit property setter."""
        infrastructure_settings._validate_max_limit = MagicMock(return_value=1000)
        infrastructure_settings.max_limit = 1000
        assert infrastructure_settings._max_limit == 1000

    def test_create(self, infrastructure_settings, mock_api_client):
        """Test create method sends folder as query parameter with payload."""
        test_data = build_settings_dict(with_id=False)
        mock_api_client.post.return_value = build_settings_dict()

        result = infrastructure_settings.create(test_data)

        # Verify the result
        assert isinstance(result, InfrastructureSettingsResponseModel)
        assert result.name == "test-infra-settings"
        assert str(result.id) == TEST_ID

        # Verify the API client was called correctly
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == infrastructure_settings.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "json" in call_args[1]
        assert "folder" not in call_args[1]["json"]

    def test_create_with_empty_response(self, infrastructure_settings, mock_api_client):
        """Test create method when the API returns 201 with no body."""
        test_data = build_settings_dict(with_id=False)
        mock_api_client.post.return_value = None

        result = infrastructure_settings.create(test_data)

        assert result is None
        mock_api_client.post.assert_called_once()

    def test_create_with_invalid_folder(self, infrastructure_settings):
        """Test create method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            infrastructure_settings.create(build_settings_dict(with_id=False), folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_update(self, infrastructure_settings, mock_api_client):
        """Test update method uses PUT with no ID in the path."""
        test_data = build_settings_dict(with_id=False)
        mock_api_client.put.return_value = build_settings_dict()

        result = infrastructure_settings.update(test_data)

        # Verify the result
        assert isinstance(result, InfrastructureSettingsResponseModel)
        assert result.name == "test-infra-settings"

        # Verify the API client was called correctly (no ID in path)
        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == infrastructure_settings.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "json" in call_args[1]

    def test_update_with_empty_response(self, infrastructure_settings, mock_api_client):
        """Test update method when the API returns 200 with no body."""
        test_data = build_settings_dict(with_id=False)
        mock_api_client.put.return_value = None

        result = infrastructure_settings.update(test_data)

        assert result is None
        mock_api_client.put.assert_called_once()

    def test_update_with_invalid_folder(self, infrastructure_settings):
        """Test update method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            infrastructure_settings.update(build_settings_dict(with_id=False), folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_list_with_empty_name(self, infrastructure_settings):
        """Test list method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            infrastructure_settings.list(name="")
        error = excinfo.value
        assert "name" in str(error.details["field"])

    def test_list_with_invalid_folder(self, infrastructure_settings):
        """Test list method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            infrastructure_settings.list(name="test", folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_list_with_list_response(self, infrastructure_settings, mock_api_client):
        """Test list method with flat list response format."""
        mock_response = [
            build_settings_dict(name="infra-settings-1"),
            build_settings_dict(name="infra-settings-2"),
        ]
        mock_api_client.get.return_value = mock_response

        result = infrastructure_settings.list(name="infra-settings-1")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, InfrastructureSettingsResponseModel) for item in result)
        assert result[0].name == "infra-settings-1"
        assert result[1].name == "infra-settings-2"

        # Verify the API client was called correctly
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == infrastructure_settings.ENDPOINT
        assert call_args[1]["params"] == {
            "name": "infra-settings-1",
            "folder": "Mobile Users",
        }

    def test_list_with_nested_list_response(self, infrastructure_settings, mock_api_client):
        """Test list method flattens the nested array response from the API."""
        mock_response = [
            [
                build_settings_dict(name="infra-settings-1"),
                build_settings_dict(name="infra-settings-2"),
            ]
        ]
        mock_api_client.get.return_value = mock_response

        result = infrastructure_settings.list(name="infra-settings-1")

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, InfrastructureSettingsResponseModel) for item in result)
        assert result[0].name == "infra-settings-1"
        assert result[1].name == "infra-settings-2"

    def test_list_with_dict_response(self, infrastructure_settings, mock_api_client):
        """Test list method with dictionary response format."""
        mock_response = {
            "data": [
                build_settings_dict(name="infra-settings-1"),
                build_settings_dict(name="infra-settings-2"),
            ]
        }
        mock_api_client.get.return_value = mock_response

        result = infrastructure_settings.list(name="infra-settings-1")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, InfrastructureSettingsResponseModel) for item in result)
        assert result[0].name == "infra-settings-1"
        assert result[1].name == "infra-settings-2"

    def test_list_with_invalid_response(self, infrastructure_settings, mock_api_client):
        """Test list method with invalid response structure."""
        mock_response = {"invalid": "response"}
        mock_api_client.get.return_value = mock_response

        with pytest.raises(InvalidObjectError) as excinfo:
            infrastructure_settings.list(name="test")
        error = excinfo.value
        assert "Response has invalid structure" in str(error.details)

    def test_fetch_with_empty_name(self, infrastructure_settings):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            infrastructure_settings.fetch("")
        error = excinfo.value
        assert "name" in str(error.details["field"])

    def test_fetch_with_invalid_folder(self, infrastructure_settings):
        """Test fetch method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            infrastructure_settings.fetch("test-name", folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_fetch_with_no_matching_settings(self, infrastructure_settings, mock_api_client):
        """Test fetch method when no matching settings are found."""
        mock_api_client.get.return_value = []

        with pytest.raises(InvalidObjectError) as excinfo:
            infrastructure_settings.fetch("non-existent")
        error = excinfo.value
        assert "No matching infrastructure settings found" in str(error.details)

    def test_fetch_with_one_matching_setting(self, infrastructure_settings, mock_api_client):
        """Test fetch method when one matching setting is found."""
        test_name = "test-infra-settings"
        mock_api_client.get.return_value = [build_settings_dict(name=test_name)]

        result = infrastructure_settings.fetch(test_name)

        # Verify the result
        assert isinstance(result, InfrastructureSettingsResponseModel)
        assert result.name == test_name

        # Verify the API client was called correctly
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == infrastructure_settings.ENDPOINT
        assert call_args[1]["params"] == {
            "name": test_name,
            "folder": "Mobile Users",
        }

    def test_fetch_with_multiple_matching_settings(
        self, infrastructure_settings, mock_api_client
    ):
        """Test fetch method when multiple matching settings are found."""
        test_name = "test-infra-settings"
        mock_api_client.get.return_value = [
            build_settings_dict(name=test_name),
            build_settings_dict(name=test_name),
        ]

        result = infrastructure_settings.fetch(test_name)

        # Verify the first match is returned and a warning is logged
        assert isinstance(result, InfrastructureSettingsResponseModel)
        assert result.name == test_name
        infrastructure_settings.logger.warning.assert_called_once()

    def test_delete(self, infrastructure_settings, mock_api_client):
        """Test delete method addresses the object by name and folder query parameters."""
        test_name = "test-infra-settings"

        infrastructure_settings.delete(test_name)

        # Verify the API client was called correctly (no ID in path)
        mock_api_client.delete.assert_called_once()
        call_args = mock_api_client.delete.call_args
        assert call_args[0][0] == infrastructure_settings.ENDPOINT
        assert call_args[1]["params"] == {
            "name": test_name,
            "folder": "Mobile Users",
        }

    def test_delete_with_empty_name(self, infrastructure_settings):
        """Test delete method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            infrastructure_settings.delete("")
        error = excinfo.value
        assert "name" in str(error.details["field"])

    def test_delete_with_invalid_folder(self, infrastructure_settings):
        """Test delete method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            infrastructure_settings.delete("test-name", folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)
