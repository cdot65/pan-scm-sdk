"""Test module for Mobile Agent Global Settings configuration service.

This module contains unit tests for the Mobile Agent Global Settings configuration service and its related models.
"""
# tests/scm/config/mobile_agent/test_global_settings.py

from unittest.mock import MagicMock, patch

import pytest

from scm.config.mobile_agent import GlobalSettings
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import GlobalSettingsResponseModel


class TestGlobalSettings:
    """Test cases for GlobalSettings mobile agent configuration."""

    @pytest.fixture
    def mock_api_client(self):
        """Test fixture for mock API client."""
        mock_client = MagicMock()
        return mock_client

    @pytest.fixture
    def global_settings(self, mock_api_client):
        """Test fixture for GlobalSettings instance."""
        # Patch the isinstance check
        with patch("scm.config.isinstance", return_value=True):
            service = GlobalSettings(mock_api_client)
            service.logger = MagicMock()
            return service

    def test_get(self, global_settings, mock_api_client):
        """Test get method for the global settings singleton."""
        mock_response = {
            "agent_version": "6.2.1",
            "manual_gateway": {
                "region": [
                    {
                        "name": "americas",
                        "locations": ["us-east-1", "us-west-201"],
                    }
                ]
            },
        }
        mock_api_client.get.return_value = mock_response

        result = global_settings.get()

        # Verify the result
        assert isinstance(result, GlobalSettingsResponseModel)
        assert result.agent_version == "6.2.1"
        assert result.manual_gateway is not None
        assert result.manual_gateway.region is not None
        assert result.manual_gateway.region[0].name == "americas"
        assert result.manual_gateway.region[0].locations == ["us-east-1", "us-west-201"]

        # Verify the API client was called correctly (no params, no ID)
        mock_api_client.get.assert_called_once_with(global_settings.ENDPOINT)

    def test_get_with_empty_settings(self, global_settings, mock_api_client):
        """Test get method when the singleton has no fields set."""
        mock_api_client.get.return_value = {}

        result = global_settings.get()

        assert isinstance(result, GlobalSettingsResponseModel)
        assert result.agent_version is None
        assert result.manual_gateway is None

    def test_get_with_invalid_response(self, global_settings, mock_api_client):
        """Test get method with a non-dictionary response."""
        mock_api_client.get.return_value = ["not", "a", "dict"]

        with pytest.raises(InvalidObjectError) as excinfo:
            global_settings.get()
        error = excinfo.value
        assert "Response is not a dictionary" in str(error.details)

    def test_get_with_invalid_field_type(self, global_settings, mock_api_client):
        """Test get method when the response fails model validation."""
        mock_api_client.get.return_value = {"agent_version": {"bad": "type"}}

        with pytest.raises(InvalidObjectError) as excinfo:
            global_settings.get()
        error = excinfo.value
        assert "Invalid response format" in str(error.message)

    def test_update(self, global_settings, mock_api_client):
        """Test update method for the global settings singleton."""
        test_data = {
            "agent_version": "6.3.0",
            "manual_gateway": {
                "region": [
                    {
                        "name": "europe",
                        "locations": ["eu-central-1"],
                    }
                ]
            },
        }
        mock_api_client.put.return_value = dict(test_data)

        result = global_settings.update(test_data)

        # Verify the result
        assert isinstance(result, GlobalSettingsResponseModel)
        assert result.agent_version == "6.3.0"

        # Verify the API client was called correctly (no ID in path)
        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == global_settings.ENDPOINT
        assert "json" in call_args[1]

    def test_update_with_empty_response(self, global_settings, mock_api_client):
        """Test update method echoes the payload when the API returns no body."""
        test_data = {"agent_version": "6.3.0"}
        mock_api_client.put.return_value = None

        result = global_settings.update(test_data)

        # The validated payload is echoed back as the response model
        assert isinstance(result, GlobalSettingsResponseModel)
        assert result.agent_version == "6.3.0"
        mock_api_client.put.assert_called_once()

    def test_update_with_empty_data(self, global_settings):
        """Test update method with empty configuration data."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            global_settings.update({})
        error = excinfo.value
        assert "Empty configuration data" in str(error.details)

    def test_update_with_invalid_data(self, global_settings):
        """Test update method with an invalid field."""
        with pytest.raises(InvalidObjectError) as excinfo:
            global_settings.update({"unknown_field": "value"})
        error = excinfo.value
        assert "Invalid global settings configuration" in str(error.message)
