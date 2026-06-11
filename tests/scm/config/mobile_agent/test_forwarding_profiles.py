"""Test module for Mobile Agent Forwarding Profiles configuration service.

This module contains unit tests for the Mobile Agent Forwarding Profiles configuration
service and its related models.
"""
# tests/scm/config/mobile_agent/test_forwarding_profiles.py

from unittest.mock import MagicMock, patch

import pytest

from scm.config.mobile_agent import ForwardingProfiles
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import ForwardingProfileResponseModel


class TestForwardingProfiles:
    """Test cases for ForwardingProfiles mobile agent configuration."""

    @pytest.fixture
    def mock_api_client(self):
        """Test fixture for mock API client."""
        mock_client = MagicMock()
        return mock_client

    @pytest.fixture
    def forwarding_profiles(self, mock_api_client):
        """Test fixture for ForwardingProfiles instance."""
        # Patch the isinstance check
        with patch("scm.config.isinstance", return_value=True):
            service = ForwardingProfiles(mock_api_client)
            service.logger = MagicMock()
            return service

    def test_init_with_default_max_limit(self, mock_api_client):
        """Test initialization with default max limit value."""
        with patch("scm.config.isinstance", return_value=True):
            service = ForwardingProfiles(mock_api_client)
            assert service._max_limit == ForwardingProfiles.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_api_client):
        """Test initialization with custom max limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 1000
            service = ForwardingProfiles(mock_api_client, max_limit=custom_limit)
            assert service._max_limit == custom_limit

    def test_validate_max_limit_with_invalid_type(self, forwarding_profiles):
        """Test validate_max_limit with invalid type."""
        with pytest.raises(InvalidObjectError) as excinfo:
            forwarding_profiles._validate_max_limit("not_an_int")
        error = excinfo.value
        assert "Invalid max_limit type" in str(error.details)

    def test_validate_max_limit_with_negative_value(self, forwarding_profiles):
        """Test validate_max_limit with negative value."""
        with pytest.raises(InvalidObjectError) as excinfo:
            forwarding_profiles._validate_max_limit(-1)
        error = excinfo.value
        assert "Invalid max_limit value" in str(error.details)

    def test_validate_max_limit_with_too_large_value(self, forwarding_profiles):
        """Test validate_max_limit with value exceeding absolute max."""
        with pytest.raises(InvalidObjectError) as excinfo:
            forwarding_profiles._validate_max_limit(ForwardingProfiles.ABSOLUTE_MAX_LIMIT + 1)
        error = excinfo.value
        assert "max_limit exceeds maximum allowed value" in str(error.details)

    def test_validate_max_limit_with_valid_value(self, forwarding_profiles):
        """Test validate_max_limit with valid value."""
        result = forwarding_profiles._validate_max_limit(1000)
        assert result == 1000

    def test_max_limit_property_getter(self, forwarding_profiles):
        """Test max_limit property getter."""
        forwarding_profiles._max_limit = 1000
        assert forwarding_profiles.max_limit == 1000

    def test_max_limit_property_setter(self, forwarding_profiles):
        """Test max_limit property setter."""
        forwarding_profiles._validate_max_limit = MagicMock(return_value=1000)
        forwarding_profiles.max_limit = 1000
        assert forwarding_profiles._max_limit == 1000

    def test_create(self, forwarding_profiles, mock_api_client):
        """Test create method for forwarding profiles."""
        test_data = {
            "name": "test-profile",
            "description": "Test forwarding profile",
            "definition_method": "rules",
            "type": {"ztna_agent": {"forwarding_rules": [{"name": "rule1"}]}},
        }
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            **test_data,
        }
        mock_api_client.post.return_value = mock_response

        result = forwarding_profiles.create(test_data)

        assert isinstance(result, ForwardingProfileResponseModel)
        assert result.name == "test-profile"
        assert str(result.id) == "123e4567-e89b-12d3-a456-426655440000"

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == forwarding_profiles.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "json" in call_args[1]
        # Folder is a query parameter, never part of the body
        assert "folder" not in call_args[1]["json"]

    def test_create_with_folder_in_data(self, forwarding_profiles, mock_api_client):
        """Test create method with folder supplied in the data dictionary."""
        test_data = {
            "name": "test-profile",
            "folder": "Mobile Users",
        }
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
        }
        mock_api_client.post.return_value = mock_response

        result = forwarding_profiles.create(test_data)

        assert isinstance(result, ForwardingProfileResponseModel)
        call_args = mock_api_client.post.call_args
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "folder" not in call_args[1]["json"]

    def test_create_with_invalid_folder(self, forwarding_profiles, mock_api_client):
        """Test create method with an invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            forwarding_profiles.create({"name": "test-profile"}, folder="Shared")
        assert "Invalid folder value" in str(excinfo.value.details)
        mock_api_client.post.assert_not_called()

    def test_get(self, forwarding_profiles, mock_api_client):
        """Test get method for fetching a forwarding profile by ID."""
        test_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": test_id,
            "name": "test-profile",
            "definition_method": "rules",
        }
        mock_api_client.get.return_value = mock_response

        result = forwarding_profiles.get(test_id)

        assert isinstance(result, ForwardingProfileResponseModel)
        assert result.name == "test-profile"

        mock_api_client.get.assert_called_once_with(
            f"{forwarding_profiles.ENDPOINT}/{test_id}"
        )

    def test_update(self, forwarding_profiles, mock_api_client):
        """Test update method for modifying a forwarding profile."""
        test_id = "123e4567-e89b-12d3-a456-426655440000"
        test_data = {
            "name": "updated-profile",
            "description": "Updated description",
        }
        mock_response = {
            "id": test_id,
            **test_data,
        }
        mock_api_client.put.return_value = mock_response

        result = forwarding_profiles.update(test_id, test_data)

        assert isinstance(result, ForwardingProfileResponseModel)
        assert result.name == "updated-profile"

        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == f"{forwarding_profiles.ENDPOINT}/{test_id}"
        assert "json" in call_args[1]

    def test_update_strips_id_from_payload(self, forwarding_profiles, mock_api_client):
        """Test that the object ID is removed from the update payload."""
        test_id = "123e4567-e89b-12d3-a456-426655440000"
        test_data = {
            "id": test_id,
            "name": "updated-profile",
        }
        mock_api_client.put.return_value = {"id": test_id, "name": "updated-profile"}

        forwarding_profiles.update(test_id, test_data)

        call_args = mock_api_client.put.call_args
        assert "id" not in call_args[1]["json"]

    def test_delete(self, forwarding_profiles, mock_api_client):
        """Test delete method for forwarding profiles."""
        test_id = "123e4567-e89b-12d3-a456-426655440000"

        forwarding_profiles.delete(test_id)

        mock_api_client.delete.assert_called_once_with(
            f"{forwarding_profiles.ENDPOINT}/{test_id}"
        )

    def test_list(self, forwarding_profiles, mock_api_client):
        """Test list method for forwarding profiles."""
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "profile1",
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "profile2",
                },
            ],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        mock_api_client.get.return_value = mock_response

        result = forwarding_profiles.list()

        assert len(result) == 2
        assert all(isinstance(item, ForwardingProfileResponseModel) for item in result)
        assert result[0].name == "profile1"

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == forwarding_profiles.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Mobile Users"

    def test_list_with_name_filter(self, forwarding_profiles, mock_api_client):
        """Test list method with server-side name filter."""
        mock_api_client.get.return_value = {"data": []}

        forwarding_profiles.list(name="profile1")

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["name"] == "profile1"

    def test_list_with_invalid_folder(self, forwarding_profiles, mock_api_client):
        """Test list method with an invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            forwarding_profiles.list(folder="Shared")
        assert "Invalid folder value" in str(excinfo.value.details)
        mock_api_client.get.assert_not_called()

    def test_list_handles_direct_list_response(self, forwarding_profiles, mock_api_client):
        """Test list method when the API returns a bare list."""
        mock_api_client.get.return_value = [
            {"id": "123e4567-e89b-12d3-a456-426655440000", "name": "profile1"},
        ]

        result = forwarding_profiles.list()

        assert len(result) == 1
        assert result[0].name == "profile1"

    def test_list_with_invalid_response(self, forwarding_profiles, mock_api_client):
        """Test list method with an unexpected response format."""
        mock_api_client.get.return_value = "not-a-valid-response"

        with pytest.raises(InvalidObjectError) as excinfo:
            forwarding_profiles.list()
        assert "Response has invalid structure" in str(excinfo.value.details)

    def test_list_pagination(self, forwarding_profiles, mock_api_client):
        """Test list method auto-pagination across multiple pages."""
        forwarding_profiles._max_limit = 2
        first_page = {
            "data": [
                {"id": "123e4567-e89b-12d3-a456-426655440000", "name": "profile1"},
                {"id": "223e4567-e89b-12d3-a456-426655440000", "name": "profile2"},
            ]
        }
        second_page = {
            "data": [
                {"id": "323e4567-e89b-12d3-a456-426655440000", "name": "profile3"},
            ]
        }
        mock_api_client.get.side_effect = [first_page, second_page]

        result = forwarding_profiles.list()

        assert len(result) == 3
        assert mock_api_client.get.call_count == 2
        second_call_params = mock_api_client.get.call_args_list[1][1]["params"]
        assert second_call_params["offset"] == 2

    def test_fetch(self, forwarding_profiles, mock_api_client):
        """Test fetch method for retrieving a profile by name."""
        mock_response = {
            "data": [
                {"id": "123e4567-e89b-12d3-a456-426655440000", "name": "test-profile"},
            ]
        }
        mock_api_client.get.return_value = mock_response

        result = forwarding_profiles.fetch(name="test-profile")

        assert isinstance(result, ForwardingProfileResponseModel)
        assert result.name == "test-profile"

    def test_fetch_with_empty_name(self, forwarding_profiles, mock_api_client):
        """Test fetch method with an empty name."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            forwarding_profiles.fetch(name="")
        assert '"name" is not allowed to be empty' in str(excinfo.value.details)

    def test_fetch_with_invalid_folder(self, forwarding_profiles, mock_api_client):
        """Test fetch method with an invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            forwarding_profiles.fetch(name="test-profile", folder="Shared")
        assert "Invalid folder value" in str(excinfo.value.details)

    def test_fetch_not_found(self, forwarding_profiles, mock_api_client):
        """Test fetch method when no profile matches."""
        mock_api_client.get.return_value = {"data": []}

        with pytest.raises(InvalidObjectError) as excinfo:
            forwarding_profiles.fetch(name="missing-profile")
        assert excinfo.value.http_status_code == 404

    def test_fetch_multiple_matches_warns(self, forwarding_profiles, mock_api_client):
        """Test fetch method warns and returns first match when multiple found."""
        mock_response = {
            "data": [
                {"id": "123e4567-e89b-12d3-a456-426655440000", "name": "test-profile"},
                {"id": "223e4567-e89b-12d3-a456-426655440000", "name": "test-profile"},
            ]
        }
        mock_api_client.get.return_value = mock_response

        result = forwarding_profiles.fetch(name="test-profile")

        assert str(result.id) == "123e4567-e89b-12d3-a456-426655440000"
        forwarding_profiles.logger.warning.assert_called_once()
