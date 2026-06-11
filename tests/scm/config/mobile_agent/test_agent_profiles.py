"""Test module for Mobile Agent Agent Profiles (Application Settings) configuration service.

This module contains unit tests for the Mobile Agent Agent Profiles configuration service.
"""
# tests/scm/config/mobile_agent/test_agent_profiles.py

from unittest.mock import MagicMock, patch

import pytest

from scm.config.mobile_agent import AgentProfiles
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import AgentProfilesResponseModel


class TestAgentProfiles:
    """Test cases for AgentProfiles mobile agent configuration."""

    @pytest.fixture
    def mock_api_client(self):
        """Test fixture for mock API client."""
        mock_client = MagicMock()
        return mock_client

    @pytest.fixture
    def agent_profiles(self, mock_api_client):
        """Test fixture for AgentProfiles instance."""
        # Patch the isinstance check
        with patch("scm.config.isinstance", return_value=True):
            service = AgentProfiles(mock_api_client)
            service.logger = MagicMock()
            return service

    def test_init_with_default_max_limit(self, mock_api_client):
        """Test initialization with default max limit value."""
        with patch("scm.config.isinstance", return_value=True):
            service = AgentProfiles(mock_api_client)
            assert service._max_limit == AgentProfiles.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_api_client):
        """Test initialization with custom max limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 1000
            service = AgentProfiles(mock_api_client, max_limit=custom_limit)
            assert service._max_limit == custom_limit

    def test_validate_max_limit_with_invalid_type(self, agent_profiles):
        """Test validate_max_limit with invalid type."""
        with pytest.raises(InvalidObjectError) as excinfo:
            agent_profiles._validate_max_limit("not_an_int")
        error = excinfo.value
        assert "Invalid max_limit type" in str(error.details)

    def test_validate_max_limit_with_negative_value(self, agent_profiles):
        """Test validate_max_limit with negative value."""
        with pytest.raises(InvalidObjectError) as excinfo:
            agent_profiles._validate_max_limit(-1)
        error = excinfo.value
        assert "Invalid max_limit value" in str(error.details)

    def test_validate_max_limit_with_too_large_value(self, agent_profiles):
        """Test validate_max_limit with value exceeding absolute max."""
        with pytest.raises(InvalidObjectError) as excinfo:
            agent_profiles._validate_max_limit(AgentProfiles.ABSOLUTE_MAX_LIMIT + 1)
        error = excinfo.value
        assert "max_limit exceeds maximum allowed value" in str(error.details)

    def test_validate_max_limit_with_valid_value(self, agent_profiles):
        """Test validate_max_limit with valid value."""
        result = agent_profiles._validate_max_limit(1000)
        assert result == 1000

    def test_max_limit_property_getter(self, agent_profiles):
        """Test max_limit property getter."""
        agent_profiles._max_limit = 1000
        assert agent_profiles.max_limit == 1000

    def test_max_limit_property_setter(self, agent_profiles):
        """Test max_limit property setter."""
        agent_profiles._validate_max_limit = MagicMock(return_value=1000)
        agent_profiles.max_limit = 1000
        assert agent_profiles._max_limit == 1000

    def test_create(self, agent_profiles, mock_api_client):
        """Test create method for agent profiles."""
        # Prepare test data
        test_data = {
            "name": "test-profile",
            "folder": "Mobile Users",
            "os": ["Windows"],
            "gp_app_config": {"config": [{"name": "connect-method", "value": ["user-logon"]}]},
        }
        mock_response = {
            "name": "test-profile",
            "folder": "Mobile Users",
            "os": ["Windows"],
            "gp_app_config": {"config": [{"name": "connect-method", "value": ["user-logon"]}]},
        }
        mock_api_client.post.return_value = mock_response

        # Call the method
        result = agent_profiles.create(test_data)

        # Verify the result
        assert isinstance(result, AgentProfilesResponseModel)
        assert result.name == "test-profile"

        # Verify the API client was called correctly: folder goes as a query parameter
        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == agent_profiles.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "json" in call_args[1]
        assert call_args[1]["json"]["name"] == "test-profile"

    def test_create_with_invalid_folder(self, agent_profiles):
        """Test create method with invalid folder raises a validation error."""
        test_data = {
            "name": "test-profile",
            "folder": "Invalid Folder",
        }
        with pytest.raises(ValueError) as excinfo:
            agent_profiles.create(test_data)
        assert "Folder must be 'Mobile Users'" in str(excinfo.value)

    def test_update(self, agent_profiles, mock_api_client):
        """Test update method for modifying agent profiles (no id in path)."""
        # Prepare test data
        test_data = {
            "name": "test-profile",
            "folder": "Mobile Users",
            "os": ["Mac"],
        }
        # The API returns 200 OK with no body for updates
        mock_api_client.put.return_value = None

        # Call the method
        result = agent_profiles.update(test_data)

        # Verify the result
        assert result is None

        # Verify the API client was called correctly: collection endpoint, folder param
        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == agent_profiles.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "json" in call_args[1]
        assert call_args[1]["json"]["name"] == "test-profile"

    def test_update_with_response_body(self, agent_profiles, mock_api_client):
        """Test update method when the API returns a body."""
        test_data = {
            "name": "test-profile",
            "folder": "Mobile Users",
        }
        mock_response = {
            "name": "test-profile",
            "folder": "Mobile Users",
            "os": ["Mac"],
        }
        mock_api_client.put.return_value = mock_response

        result = agent_profiles.update(test_data)

        assert isinstance(result, AgentProfilesResponseModel)
        assert result.name == "test-profile"

    def test_update_with_missing_folder(self, agent_profiles):
        """Test update method without folder raises a validation error."""
        with pytest.raises(ValueError) as excinfo:
            agent_profiles.update({"name": "test-profile"})
        assert "Folder is required" in str(excinfo.value)

    def test_list_with_invalid_folder(self, agent_profiles):
        """Test list method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            agent_profiles.list(folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_list_with_list_response(self, agent_profiles, mock_api_client):
        """Test list method with list response format."""
        # Prepare test data
        mock_response = [
            {"name": "profile-1", "folder": "Mobile Users"},
            {"name": "profile-2", "folder": "Mobile Users"},
        ]
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = agent_profiles.list()

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, AgentProfilesResponseModel) for item in result)
        assert result[0].name == "profile-1"
        assert result[1].name == "profile-2"

        # Verify the API client was called correctly
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == agent_profiles.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Mobile Users"
        assert call_args[1]["params"]["limit"] == agent_profiles.max_limit
        assert call_args[1]["params"]["offset"] == 0

    def test_list_with_dict_response(self, agent_profiles, mock_api_client):
        """Test list method with dictionary response format."""
        # Prepare test data
        mock_response = {
            "data": [
                {"name": "profile-1", "folder": "Mobile Users"},
                {"name": "profile-2", "folder": "Mobile Users"},
            ],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = agent_profiles.list()

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, AgentProfilesResponseModel) for item in result)
        assert result[0].name == "profile-1"
        assert result[1].name == "profile-2"

    def test_list_with_name_filter(self, agent_profiles, mock_api_client):
        """Test list method passes the name filter server-side."""
        mock_api_client.get.return_value = {"data": []}

        agent_profiles.list(name="profile-1")

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["name"] == "profile-1"

    def test_list_with_pagination(self, agent_profiles, mock_api_client):
        """Test list method auto-paginates dict responses."""
        agent_profiles._max_limit = 2
        first_page = {
            "data": [
                {"name": "profile-1", "folder": "Mobile Users"},
                {"name": "profile-2", "folder": "Mobile Users"},
            ]
        }
        second_page = {
            "data": [
                {"name": "profile-3", "folder": "Mobile Users"},
            ]
        }
        mock_api_client.get.side_effect = [first_page, second_page]

        result = agent_profiles.list()

        assert len(result) == 3
        assert mock_api_client.get.call_count == 2
        second_call_params = mock_api_client.get.call_args_list[1][1]["params"]
        assert second_call_params["offset"] == 2

    def test_list_with_invalid_response(self, agent_profiles, mock_api_client):
        """Test list method with invalid response structure."""
        # Prepare test data
        mock_response = {"invalid": "response"}
        mock_api_client.get.return_value = mock_response

        # Call the method
        with pytest.raises(InvalidObjectError) as excinfo:
            agent_profiles.list()
        error = excinfo.value
        assert "Response has invalid structure" in str(error.details)

    def test_fetch_with_empty_name(self, agent_profiles):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            agent_profiles.fetch("")
        error = excinfo.value
        assert "name" in str(error.details["field"])

    def test_fetch_with_invalid_folder(self, agent_profiles):
        """Test fetch method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            agent_profiles.fetch("test-name", folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)

    def test_fetch_with_no_matching_profiles(self, agent_profiles, mock_api_client):
        """Test fetch method when no matching profiles are found."""
        # Prepare test data
        mock_api_client.get.return_value = []

        # Call the method
        with pytest.raises(InvalidObjectError) as excinfo:
            agent_profiles.fetch("non-existent")
        error = excinfo.value
        assert "No matching agent profile found" in str(error.details)

    def test_fetch_with_one_matching_profile(self, agent_profiles, mock_api_client):
        """Test fetch method when one matching profile is found."""
        # Prepare test data
        test_name = "test-profile"
        mock_response = [
            {"name": test_name, "folder": "Mobile Users"},
        ]
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = agent_profiles.fetch(test_name)

        # Verify the result
        assert isinstance(result, AgentProfilesResponseModel)
        assert result.name == test_name

        # Verify the API client was called correctly: name passed server-side
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == agent_profiles.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Mobile Users"
        assert call_args[1]["params"]["name"] == test_name

    def test_fetch_with_multiple_matching_profiles(self, agent_profiles, mock_api_client):
        """Test fetch method when multiple matching profiles are found."""
        # Prepare test data
        test_name = "test-profile"
        mock_response = [
            {"name": test_name, "folder": "Mobile Users", "os": ["Windows"]},
            {"name": test_name, "folder": "Mobile Users", "os": ["Mac"]},
        ]
        mock_api_client.get.return_value = mock_response

        # Call the method
        result = agent_profiles.fetch(test_name)

        # Verify the result: should return the first match
        assert isinstance(result, AgentProfilesResponseModel)
        assert result.name == test_name
        assert result.os[0] == "Windows"

    def test_delete(self, agent_profiles, mock_api_client):
        """Test delete method for removing agent profiles by name."""
        # Call the method
        agent_profiles.delete("test-profile")

        # Verify the API client was called correctly: name+folder as query parameters
        mock_api_client.delete.assert_called_once_with(
            agent_profiles.ENDPOINT,
            params={"name": "test-profile", "folder": "Mobile Users"},
        )

    def test_delete_with_empty_name(self, agent_profiles):
        """Test delete method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            agent_profiles.delete("")
        error = excinfo.value
        assert "name" in str(error.details["field"])

    def test_delete_with_invalid_folder(self, agent_profiles):
        """Test delete method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            agent_profiles.delete("test-profile", folder="Invalid")
        error = excinfo.value
        assert "Invalid folder value" in str(error.details)
