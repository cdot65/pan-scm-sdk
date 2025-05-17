"""Test module for Mobile Agent Auth Settings configuration service.

This module contains unit tests for the Mobile Agent Auth Settings configuration service and its related models.
"""
# tests/scm/config/mobile_agent/test_auth_settings.py

from unittest.mock import MagicMock, patch

import pytest

from scm.config.mobile_agent import AuthSettings
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import AuthSettingsResponseModel


class TestAuthSettings:
    """Test cases for AuthSettings mobile agent configuration."""

    @pytest.fixture
    def mock_api_client(self):
        """Test fixture for mock API client."""
        mock_client = MagicMock()
        return mock_client

    @pytest.fixture
    def auth_settings(self, mock_api_client):
        """Test fixture for AuthSettings instance."""
        # Patch the isinstance check
        with patch("scm.config.isinstance", return_value=True):
            service = AuthSettings(mock_api_client)
            service.logger = MagicMock()
            return service

    def test_init_with_default_max_limit(self, mock_api_client):
        """Test initialization with default max limit value."""
        with patch("scm.config.isinstance", return_value=True):
            service = AuthSettings(mock_api_client)
            assert service._max_limit == AuthSettings.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_api_client):
        """Test initialization with custom max limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 1000
            service = AuthSettings(mock_api_client, max_limit=custom_limit)
            assert service._max_limit == custom_limit

    def test_validate_max_limit_with_invalid_type(self, auth_settings):
        """Test validate_max_limit with invalid type."""
        with pytest.raises(InvalidObjectError) as excinfo:
            auth_settings._validate_max_limit("not_an_int")
        error = excinfo.value
        assert "Invalid max_limit type" in str(error.details)

    def test_validate_max_limit_with_negative_value(self, auth_settings):
        """Test validate_max_limit with negative value."""
        with pytest.raises(InvalidObjectError) as excinfo:
            auth_settings._validate_max_limit(-1)
        error = excinfo.value
        assert "Invalid max_limit value" in str(error.details)

    def test_validate_max_limit_with_too_large_value(self, auth_settings):
        """Test validate_max_limit with value exceeding absolute max."""
        with pytest.raises(InvalidObjectError) as excinfo:
            auth_settings._validate_max_limit(AuthSettings.ABSOLUTE_MAX_LIMIT + 1)
        error = excinfo.value
        assert "max_limit exceeds maximum allowed value" in str(error.details)

    def test_validate_max_limit_with_valid_value(self, auth_settings):
        """Test validate_max_limit with valid value."""
        result = auth_settings._validate_max_limit(1000)
        assert result == 1000

    def test_max_limit_property_getter(self, auth_settings):
        """Test max_limit property getter."""
        auth_settings._max_limit = 1000
        assert auth_settings.max_limit == 1000

    def test_max_limit_property_setter(self, auth_settings):
        """Test max_limit property setter."""
        auth_settings._validate_max_limit = MagicMock(return_value=1000)
        auth_settings.max_limit = 1000
        assert auth_settings._max_limit == 1000

    def test_create(self, auth_settings, mock_api_client):
        """Test create method for auth settings."""
        # Prepare test data
        test_data = {
            "name": "test-auth-settings",
            "authentication_profile": "test-profile",
            "user_credential_or_client_cert_required": True,
            "folder": "Mobile Users",
        }
        mock_response = {
            "name": "test-auth-settings",
            "authentication_profile": "test-profile",
            "user_credential_or_client_cert_required": True,
            "folder": "Mobile Users",
        }
        mock_api_client.post.return_value = mock_response

        # Call the method
        result = auth_settings.create(test_data)

        # Verify the result
        assert isinstance(result, AuthSettingsResponseModel)
        assert result.name == "test-auth-settings"

        # Verify the API client was called correctly
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == auth_settings.ENDPOINT
        assert "json" in call_args[1]

    def test_get(self, auth_settings, mock_api_client):
        """Test get method for fetching auth settings by ID."""
        # Prepare test data
        test_id = "test-id"
        mock_response = {
            "name": "test-auth-settings",
            "authentication_profile": "test-profile",
            "user_credential_or_client_cert_required": True,
            "folder": "Mobile Users",
        }
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = auth_settings.get(test_id)

        # Verify the result
        assert isinstance(result, AuthSettingsResponseModel)
        assert result.name == "test-auth-settings"

        # Verify the API client was called correctly
        mock_api_client.get.assert_called_once_with(f"{auth_settings.ENDPOINT}/{test_id}")

    def test_update(self, auth_settings, mock_api_client):
        """Test update method for modifying auth settings."""
        # Prepare test data
        test_id = "test-id"
        test_data = {
            "name": "updated-auth-settings",
            "authentication_profile": "updated-profile",
        }
        mock_response = {
            "name": "updated-auth-settings",
            "authentication_profile": "updated-profile",
            "user_credential_or_client_cert_required": True,
            "folder": "Mobile Users",
        }
        mock_api_client.put.return_value = mock_response

        # Call the method
        result = auth_settings.update(test_id, test_data)

        # Verify the result
        assert isinstance(result, AuthSettingsResponseModel)
        assert result.name == "updated-auth-settings"

        # Verify the API client was called correctly
        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == f"{auth_settings.ENDPOINT}/{test_id}"
        assert "json" in call_args[1]

    def test_move(self, auth_settings, mock_api_client):
        """Test move method for repositioning auth settings."""
        # Prepare test data
        test_move_data = {
            "name": "test-auth-settings",
            "where": "top",
        }

        # Call the method
        auth_settings.move(test_move_data)

        # Verify the API client was called correctly
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == f"{auth_settings.ENDPOINT}/move"
        assert "json" in call_args[1]

    def test_list_with_invalid_folder(self, auth_settings):
        """Test list method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            auth_settings.list(folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_list_with_list_response(self, auth_settings, mock_api_client):
        """Test list method with list response format."""
        # Prepare test data
        mock_response = [
            {
                "name": "auth-settings-1",
                "authentication_profile": "profile-1",
                "user_credential_or_client_cert_required": True,
                "folder": "Mobile Users",
            },
            {
                "name": "auth-settings-2",
                "authentication_profile": "profile-2",
                "user_credential_or_client_cert_required": False,
                "folder": "Mobile Users",
            },
        ]
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = auth_settings.list()

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, AuthSettingsResponseModel) for item in result)
        assert result[0].name == "auth-settings-1"
        assert result[1].name == "auth-settings-2"

        # Verify the API client was called correctly
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == auth_settings.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}

    def test_list_with_dict_response(self, auth_settings, mock_api_client):
        """Test list method with dictionary response format."""
        # Prepare test data
        mock_response = {
            "data": [
                {
                    "name": "auth-settings-1",
                    "authentication_profile": "profile-1",
                    "user_credential_or_client_cert_required": True,
                    "folder": "Mobile Users",
                },
                {
                    "name": "auth-settings-2",
                    "authentication_profile": "profile-2",
                    "user_credential_or_client_cert_required": False,
                    "folder": "Mobile Users",
                },
            ]
        }
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = auth_settings.list()

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, AuthSettingsResponseModel) for item in result)
        assert result[0].name == "auth-settings-1"
        assert result[1].name == "auth-settings-2"

        # Verify the API client was called correctly
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == auth_settings.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}

    def test_list_with_invalid_response(self, auth_settings, mock_api_client):
        """Test list method with invalid response structure."""
        # Prepare test data
        mock_response = {"invalid": "response"}
        mock_api_client.get.return_value = mock_response

        # Call the method
        with pytest.raises(InvalidObjectError) as excinfo:
            auth_settings.list()
        error = excinfo.value
        assert "Response has invalid structure" in str(error.details)

    def test_fetch_with_empty_name(self, auth_settings):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            auth_settings.fetch("")
        error = excinfo.value
        assert "name" in str(error.details["field"])

    def test_fetch_with_invalid_folder(self, auth_settings):
        """Test fetch method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            auth_settings.fetch("test-name", folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_fetch_with_no_matching_settings(self, auth_settings, mock_api_client):
        """Test fetch method when no matching settings are found."""
        # Prepare test data
        mock_api_client.get.return_value = []

        # Call the method
        with pytest.raises(InvalidObjectError) as excinfo:
            auth_settings.fetch("non-existent")
        error = excinfo.value
        assert "No matching authentication settings found" in str(error.details)

    def test_fetch_with_one_matching_setting(self, auth_settings, mock_api_client):
        """Test fetch method when one matching setting is found."""
        # Prepare test data
        test_name = "test-auth-settings"
        mock_response = [
            {
                "name": test_name,
                "authentication_profile": "test-profile",
                "user_credential_or_client_cert_required": True,
                "folder": "Mobile Users",
            },
        ]
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = auth_settings.fetch(test_name)

        # Verify the result
        assert isinstance(result, AuthSettingsResponseModel)
        assert result.name == test_name

        # Verify the API client was called correctly
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == auth_settings.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}

    def test_fetch_with_multiple_matching_settings(self, auth_settings, mock_api_client):
        """Test fetch method when multiple matching settings are found."""
        # Prepare test data
        test_name = "test-auth-settings"
        mock_response = [
            {
                "name": test_name,
                "authentication_profile": "profile-1",
                "user_credential_or_client_cert_required": True,
                "folder": "Mobile Users",
            },
            {
                "name": test_name,
                "authentication_profile": "profile-2",
                "user_credential_or_client_cert_required": False,
                "folder": "Mobile Users",
            },
        ]
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = auth_settings.fetch(test_name)

        # Verify the result
        assert isinstance(result, AuthSettingsResponseModel)
        assert result.name == test_name
        assert result.authentication_profile == "profile-1"  # Should return the first match

        # Verify the API client was called correctly
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == auth_settings.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}

    def test_delete(self, auth_settings, mock_api_client):
        """Test delete method for removing auth settings."""
        # Prepare test data
        test_id = "test-id"

        # Call the method
        auth_settings.delete(test_id)

        # Verify the API client was called correctly
        mock_api_client.delete.assert_called_once_with(f"{auth_settings.ENDPOINT}/{test_id}")
