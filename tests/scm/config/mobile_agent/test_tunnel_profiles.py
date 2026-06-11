"""Test module for Mobile Agent Tunnel Profiles configuration service.

This module contains unit tests for the Mobile Agent Tunnel Profiles configuration
service and its related models.
"""
# tests/scm/config/mobile_agent/test_tunnel_profiles.py

from unittest.mock import MagicMock, patch

import pytest

from scm.config.mobile_agent import TunnelProfiles
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import TunnelProfileResponseModel


class TestTunnelProfiles:
    """Test cases for TunnelProfiles mobile agent configuration."""

    @pytest.fixture
    def mock_api_client(self):
        """Test fixture for mock API client."""
        mock_client = MagicMock()
        return mock_client

    @pytest.fixture
    def tunnel_profiles(self, mock_api_client):
        """Test fixture for TunnelProfiles instance."""
        # Patch the isinstance check
        with patch("scm.config.isinstance", return_value=True):
            service = TunnelProfiles(mock_api_client)
            service.logger = MagicMock()
            return service

    def test_init_with_default_max_limit(self, mock_api_client):
        """Test initialization with default max limit value."""
        with patch("scm.config.isinstance", return_value=True):
            service = TunnelProfiles(mock_api_client)
            assert service._max_limit == TunnelProfiles.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_api_client):
        """Test initialization with custom max limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 1000
            service = TunnelProfiles(mock_api_client, max_limit=custom_limit)
            assert service._max_limit == custom_limit

    def test_validate_max_limit_with_invalid_type(self, tunnel_profiles):
        """Test validate_max_limit with invalid type."""
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel_profiles._validate_max_limit("not_an_int")
        error = excinfo.value
        assert "Invalid max_limit type" in str(error.details)

    def test_validate_max_limit_with_negative_value(self, tunnel_profiles):
        """Test validate_max_limit with negative value."""
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel_profiles._validate_max_limit(-1)
        error = excinfo.value
        assert "Invalid max_limit value" in str(error.details)

    def test_validate_max_limit_with_too_large_value(self, tunnel_profiles):
        """Test validate_max_limit with value exceeding absolute max."""
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel_profiles._validate_max_limit(TunnelProfiles.ABSOLUTE_MAX_LIMIT + 1)
        error = excinfo.value
        assert "max_limit exceeds maximum allowed value" in str(error.details)

    def test_validate_max_limit_with_valid_value(self, tunnel_profiles):
        """Test validate_max_limit with valid value."""
        result = tunnel_profiles._validate_max_limit(1000)
        assert result == 1000

    def test_max_limit_property_getter(self, tunnel_profiles):
        """Test max_limit property getter."""
        tunnel_profiles._max_limit = 1000
        assert tunnel_profiles.max_limit == 1000

    def test_max_limit_property_setter(self, tunnel_profiles):
        """Test max_limit property setter."""
        tunnel_profiles._validate_max_limit = MagicMock(return_value=1000)
        tunnel_profiles.max_limit = 1000
        assert tunnel_profiles._max_limit == 1000

    def test_create(self, tunnel_profiles, mock_api_client):
        """Test create method for tunnel profiles."""
        # Prepare test data
        test_data = {
            "name": "test-tunnel",
            "os": ["Windows", "Mac"],
            "no_direct_access_to_local_network": True,
        }
        mock_response = {
            "name": "test-tunnel",
            "os": ["Windows", "Mac"],
            "no_direct_access_to_local_network": True,
            "folder": "Mobile Users",
        }
        mock_api_client.post.return_value = mock_response

        # Call the method
        result = tunnel_profiles.create(test_data)

        # Verify the result
        assert isinstance(result, TunnelProfileResponseModel)
        assert result.name == "test-tunnel"

        # Verify the API client was called correctly
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == tunnel_profiles.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "json" in call_args[1]
        assert call_args[1]["json"]["name"] == "test-tunnel"

    def test_create_with_invalid_folder(self, tunnel_profiles):
        """Test create method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel_profiles.create({"name": "test-tunnel"}, folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_create_with_nested_configuration(self, tunnel_profiles, mock_api_client):
        """Test create method with nested split tunneling configuration."""
        test_data = {
            "name": "test-tunnel",
            "split_tunneling": {
                "access_route": ["10.1.0.0/16"],
                "exclude_domains": {"list": [{"name": "example.com", "ports": [443]}]},
            },
        }
        mock_response = {**test_data, "folder": "Mobile Users"}
        mock_api_client.post.return_value = mock_response

        result = tunnel_profiles.create(test_data)

        assert isinstance(result, TunnelProfileResponseModel)
        assert result.split_tunneling.access_route == ["10.1.0.0/16"]
        assert result.split_tunneling.exclude_domains.list[0].name == "example.com"

    def test_update(self, tunnel_profiles, mock_api_client):
        """Test update method for modifying tunnel profiles."""
        # Prepare test data
        test_data = {
            "name": "test-tunnel",
            "retrieve_framed_ip_address": True,
        }
        mock_response = {
            "name": "test-tunnel",
            "retrieve_framed_ip_address": True,
            "folder": "Mobile Users",
        }
        mock_api_client.put.return_value = mock_response

        # Call the method
        result = tunnel_profiles.update(test_data)

        # Verify the result
        assert isinstance(result, TunnelProfileResponseModel)
        assert result.name == "test-tunnel"

        # Verify the API client was called correctly: no ID in the URL,
        # object addressed by name in body + folder query param
        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == tunnel_profiles.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "json" in call_args[1]
        assert call_args[1]["json"]["name"] == "test-tunnel"

    def test_update_with_invalid_folder(self, tunnel_profiles):
        """Test update method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel_profiles.update({"name": "test-tunnel"}, folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_list_with_invalid_folder(self, tunnel_profiles):
        """Test list method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel_profiles.list(folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_list_with_list_response(self, tunnel_profiles, mock_api_client):
        """Test list method with list response format."""
        # Prepare test data
        mock_response = [
            {"name": "tunnel-1", "os": ["Windows"], "folder": "Mobile Users"},
            {"name": "tunnel-2", "os": ["Mac"], "folder": "Mobile Users"},
        ]
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = tunnel_profiles.list()

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, TunnelProfileResponseModel) for item in result)
        assert result[0].name == "tunnel-1"
        assert result[1].name == "tunnel-2"

        # Verify the API client was called correctly
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == tunnel_profiles.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Mobile Users"

    def test_list_with_dict_response(self, tunnel_profiles, mock_api_client):
        """Test list method with dictionary response format."""
        # Prepare test data
        mock_response = {
            "data": [
                {"name": "tunnel-1", "os": ["Windows"], "folder": "Mobile Users"},
                {"name": "tunnel-2", "os": ["Mac"], "folder": "Mobile Users"},
            ],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = tunnel_profiles.list()

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, TunnelProfileResponseModel) for item in result)
        assert result[0].name == "tunnel-1"
        assert result[1].name == "tunnel-2"

        # Verify the API client was called correctly
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == tunnel_profiles.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Mobile Users"

    def test_list_with_name_filter(self, tunnel_profiles, mock_api_client):
        """Test list method passes the server-side name filter."""
        mock_api_client.get.return_value = {"data": []}

        tunnel_profiles.list(name="tunnel-1")

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["name"] == "tunnel-1"

    def test_list_pagination(self, tunnel_profiles, mock_api_client):
        """Test list method paginates through multiple pages."""
        tunnel_profiles._max_limit = 2
        page_one = {
            "data": [
                {"name": "tunnel-1", "folder": "Mobile Users"},
                {"name": "tunnel-2", "folder": "Mobile Users"},
            ]
        }
        page_two = {"data": [{"name": "tunnel-3", "folder": "Mobile Users"}]}
        mock_api_client.get.side_effect = [page_one, page_two]

        result = tunnel_profiles.list()

        assert len(result) == 3
        assert mock_api_client.get.call_count == 2
        first_call_params = mock_api_client.get.call_args_list[0][1]["params"]
        second_call_params = mock_api_client.get.call_args_list[1][1]["params"]
        assert first_call_params["offset"] == 0
        assert second_call_params["offset"] == 2

    def test_list_with_invalid_response(self, tunnel_profiles, mock_api_client):
        """Test list method with invalid response structure."""
        # Prepare test data
        mock_response = {"invalid": "response"}
        mock_api_client.get.return_value = mock_response

        # Call the method
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel_profiles.list()
        error = excinfo.value
        assert "Response has invalid structure" in str(error.details)

    def test_fetch_with_empty_name(self, tunnel_profiles):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            tunnel_profiles.fetch("")
        error = excinfo.value
        assert "name" in str(error.details["field"])

    def test_fetch_with_invalid_folder(self, tunnel_profiles):
        """Test fetch method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel_profiles.fetch("test-name", folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_fetch_with_no_matching_profiles(self, tunnel_profiles, mock_api_client):
        """Test fetch method when no matching profiles are found."""
        # Prepare test data
        mock_api_client.get.return_value = []

        # Call the method
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel_profiles.fetch("non-existent")
        error = excinfo.value
        assert "No matching tunnel profile found" in str(error.details)

    def test_fetch_with_one_matching_profile(self, tunnel_profiles, mock_api_client):
        """Test fetch method when one matching profile is found."""
        # Prepare test data
        test_name = "test-tunnel"
        mock_response = [
            {"name": test_name, "os": ["Windows"], "folder": "Mobile Users"},
        ]
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = tunnel_profiles.fetch(test_name)

        # Verify the result
        assert isinstance(result, TunnelProfileResponseModel)
        assert result.name == test_name

        # Verify the API client was called correctly with the server-side name filter
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == tunnel_profiles.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Mobile Users"
        assert call_args[1]["params"]["name"] == test_name

    def test_fetch_with_multiple_matching_profiles(self, tunnel_profiles, mock_api_client):
        """Test fetch method when multiple matching profiles are found."""
        # Prepare test data
        test_name = "test-tunnel"
        mock_response = [
            {"name": test_name, "os": ["Windows"], "folder": "Mobile Users"},
            {"name": test_name, "os": ["Mac"], "folder": "Mobile Users"},
        ]
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = tunnel_profiles.fetch(test_name)

        # Verify the result: should return the first match
        assert isinstance(result, TunnelProfileResponseModel)
        assert result.name == test_name
        assert result.os[0].value == "Windows"

    def test_delete(self, tunnel_profiles, mock_api_client):
        """Test delete method for removing tunnel profiles."""
        # Prepare test data
        test_name = "test-tunnel"

        # Call the method
        tunnel_profiles.delete(test_name)

        # Verify the API client was called correctly: name + folder query params, no ID path
        mock_api_client.delete.assert_called_once_with(
            tunnel_profiles.ENDPOINT,
            params={"name": test_name, "folder": "Mobile Users"},
        )

    def test_delete_with_empty_name(self, tunnel_profiles):
        """Test delete method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            tunnel_profiles.delete("")
        error = excinfo.value
        assert "name" in str(error.details["field"])

    def test_delete_with_invalid_folder(self, tunnel_profiles):
        """Test delete method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            tunnel_profiles.delete("test-tunnel", folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)
