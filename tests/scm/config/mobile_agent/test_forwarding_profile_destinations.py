"""Test module for Mobile Agent Forwarding Profile Destinations configuration service.

This module contains unit tests for the Mobile Agent Forwarding Profile Destinations
configuration service and its related models.
"""
# tests/scm/config/mobile_agent/test_forwarding_profile_destinations.py

from unittest.mock import MagicMock, patch

import pytest

from scm.config.mobile_agent import ForwardingProfileDestinations
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import ForwardingProfileDestinationResponseModel


class TestForwardingProfileDestinations:
    """Test cases for ForwardingProfileDestinations mobile agent configuration."""

    @pytest.fixture
    def mock_api_client(self):
        """Test fixture for mock API client."""
        mock_client = MagicMock()
        return mock_client

    @pytest.fixture
    def destinations(self, mock_api_client):
        """Test fixture for ForwardingProfileDestinations instance."""
        # Patch the isinstance check
        with patch("scm.config.isinstance", return_value=True):
            service = ForwardingProfileDestinations(mock_api_client)
            service.logger = MagicMock()
            return service

    def test_init_with_default_max_limit(self, mock_api_client):
        """Test initialization with default max limit value."""
        with patch("scm.config.isinstance", return_value=True):
            service = ForwardingProfileDestinations(mock_api_client)
            assert service._max_limit == ForwardingProfileDestinations.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_api_client):
        """Test initialization with custom max limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 1000
            service = ForwardingProfileDestinations(mock_api_client, max_limit=custom_limit)
            assert service._max_limit == custom_limit

    def test_validate_max_limit_with_invalid_type(self, destinations):
        """Test validate_max_limit with invalid type."""
        with pytest.raises(InvalidObjectError) as excinfo:
            destinations._validate_max_limit("not_an_int")
        error = excinfo.value
        assert "Invalid max_limit type" in str(error.details)

    def test_validate_max_limit_with_negative_value(self, destinations):
        """Test validate_max_limit with negative value."""
        with pytest.raises(InvalidObjectError) as excinfo:
            destinations._validate_max_limit(-1)
        error = excinfo.value
        assert "Invalid max_limit value" in str(error.details)

    def test_validate_max_limit_with_too_large_value(self, destinations):
        """Test validate_max_limit with value exceeding absolute max."""
        with pytest.raises(InvalidObjectError) as excinfo:
            destinations._validate_max_limit(
                ForwardingProfileDestinations.ABSOLUTE_MAX_LIMIT + 1
            )
        error = excinfo.value
        assert "max_limit exceeds maximum allowed value" in str(error.details)

    def test_validate_max_limit_with_valid_value(self, destinations):
        """Test validate_max_limit with valid value."""
        result = destinations._validate_max_limit(1000)
        assert result == 1000

    def test_max_limit_property_getter(self, destinations):
        """Test max_limit property getter."""
        destinations._max_limit = 1000
        assert destinations.max_limit == 1000

    def test_max_limit_property_setter(self, destinations):
        """Test max_limit property setter."""
        destinations._validate_max_limit = MagicMock(return_value=1000)
        destinations.max_limit = 1000
        assert destinations._max_limit == 1000

    def test_create(self, destinations, mock_api_client):
        """Test create method for destinations."""
        test_data = {
            "name": "test-destination",
            "description": "Test destination",
            "fqdn": [{"name": "*.example.com", "port": 443}],
            "ip_addresses": [{"name": "10.0.0.0/8"}],
        }
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            **test_data,
        }
        mock_api_client.post.return_value = mock_response

        result = destinations.create(test_data)

        assert isinstance(result, ForwardingProfileDestinationResponseModel)
        assert result.name == "test-destination"
        assert str(result.id) == "123e4567-e89b-12d3-a456-426655440000"

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == destinations.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "json" in call_args[1]
        # Folder is a query parameter, never part of the body
        assert "folder" not in call_args[1]["json"]

    def test_create_with_folder_in_data(self, destinations, mock_api_client):
        """Test create method with folder supplied in the data dictionary."""
        test_data = {
            "name": "test-destination",
            "folder": "Mobile Users",
        }
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-destination",
        }
        mock_api_client.post.return_value = mock_response

        result = destinations.create(test_data)

        assert isinstance(result, ForwardingProfileDestinationResponseModel)
        call_args = mock_api_client.post.call_args
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "folder" not in call_args[1]["json"]

    def test_create_with_invalid_folder(self, destinations, mock_api_client):
        """Test create method with an invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            destinations.create({"name": "test-destination"}, folder="Shared")
        assert "Invalid folder value" in str(excinfo.value.details)
        mock_api_client.post.assert_not_called()

    def test_get(self, destinations, mock_api_client):
        """Test get method for fetching a destination by ID."""
        test_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": test_id,
            "name": "test-destination",
        }
        mock_api_client.get.return_value = mock_response

        result = destinations.get(test_id)

        assert isinstance(result, ForwardingProfileDestinationResponseModel)
        assert result.name == "test-destination"

        mock_api_client.get.assert_called_once_with(f"{destinations.ENDPOINT}/{test_id}")

    def test_update(self, destinations, mock_api_client):
        """Test update method for modifying a destination."""
        test_id = "123e4567-e89b-12d3-a456-426655440000"
        test_data = {
            "name": "updated-destination",
            "fqdn": [{"name": "*.corp.example.com"}],
        }
        mock_response = {
            "id": test_id,
            **test_data,
        }
        mock_api_client.put.return_value = mock_response

        result = destinations.update(test_id, test_data)

        assert isinstance(result, ForwardingProfileDestinationResponseModel)
        assert result.name == "updated-destination"

        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == f"{destinations.ENDPOINT}/{test_id}"
        assert "json" in call_args[1]

    def test_update_strips_id_from_payload(self, destinations, mock_api_client):
        """Test that the object ID is removed from the update payload."""
        test_id = "123e4567-e89b-12d3-a456-426655440000"
        test_data = {
            "id": test_id,
            "name": "updated-destination",
        }
        mock_api_client.put.return_value = {"id": test_id, "name": "updated-destination"}

        destinations.update(test_id, test_data)

        call_args = mock_api_client.put.call_args
        assert "id" not in call_args[1]["json"]

    def test_delete(self, destinations, mock_api_client):
        """Test delete method for destinations."""
        test_id = "123e4567-e89b-12d3-a456-426655440000"

        destinations.delete(test_id)

        mock_api_client.delete.assert_called_once_with(f"{destinations.ENDPOINT}/{test_id}")

    def test_list(self, destinations, mock_api_client):
        """Test list method for destinations."""
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "destination1",
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "destination2",
                },
            ],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        mock_api_client.get.return_value = mock_response

        result = destinations.list()

        assert len(result) == 2
        assert all(
            isinstance(item, ForwardingProfileDestinationResponseModel) for item in result
        )
        assert result[0].name == "destination1"

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == destinations.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Mobile Users"

    def test_list_with_name_filter(self, destinations, mock_api_client):
        """Test list method with server-side name filter."""
        mock_api_client.get.return_value = {"data": []}

        destinations.list(name="destination1")

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["name"] == "destination1"

    def test_list_with_invalid_folder(self, destinations, mock_api_client):
        """Test list method with an invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            destinations.list(folder="Shared")
        assert "Invalid folder value" in str(excinfo.value.details)
        mock_api_client.get.assert_not_called()

    def test_list_handles_direct_list_response(self, destinations, mock_api_client):
        """Test list method when the API returns a bare list."""
        mock_api_client.get.return_value = [
            {"id": "123e4567-e89b-12d3-a456-426655440000", "name": "destination1"},
        ]

        result = destinations.list()

        assert len(result) == 1
        assert result[0].name == "destination1"

    def test_list_with_invalid_response(self, destinations, mock_api_client):
        """Test list method with an unexpected response format."""
        mock_api_client.get.return_value = "not-a-valid-response"

        with pytest.raises(InvalidObjectError) as excinfo:
            destinations.list()
        assert "Response has invalid structure" in str(excinfo.value.details)

    def test_list_pagination(self, destinations, mock_api_client):
        """Test list method auto-pagination across multiple pages."""
        destinations._max_limit = 2
        first_page = {
            "data": [
                {"id": "123e4567-e89b-12d3-a456-426655440000", "name": "destination1"},
                {"id": "223e4567-e89b-12d3-a456-426655440000", "name": "destination2"},
            ]
        }
        second_page = {
            "data": [
                {"id": "323e4567-e89b-12d3-a456-426655440000", "name": "destination3"},
            ]
        }
        mock_api_client.get.side_effect = [first_page, second_page]

        result = destinations.list()

        assert len(result) == 3
        assert mock_api_client.get.call_count == 2
        second_call_params = mock_api_client.get.call_args_list[1][1]["params"]
        assert second_call_params["offset"] == 2

    def test_fetch(self, destinations, mock_api_client):
        """Test fetch method for retrieving a destination by name."""
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-destination",
                },
            ]
        }
        mock_api_client.get.return_value = mock_response

        result = destinations.fetch(name="test-destination")

        assert isinstance(result, ForwardingProfileDestinationResponseModel)
        assert result.name == "test-destination"

    def test_fetch_with_empty_name(self, destinations, mock_api_client):
        """Test fetch method with an empty name."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            destinations.fetch(name="")
        assert '"name" is not allowed to be empty' in str(excinfo.value.details)

    def test_fetch_with_invalid_folder(self, destinations, mock_api_client):
        """Test fetch method with an invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            destinations.fetch(name="test-destination", folder="Shared")
        assert "Invalid folder value" in str(excinfo.value.details)

    def test_fetch_not_found(self, destinations, mock_api_client):
        """Test fetch method when no destination matches."""
        mock_api_client.get.return_value = {"data": []}

        with pytest.raises(InvalidObjectError) as excinfo:
            destinations.fetch(name="missing-destination")
        assert excinfo.value.http_status_code == 404

    def test_fetch_multiple_matches_warns(self, destinations, mock_api_client):
        """Test fetch method warns and returns first match when multiple found."""
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-destination",
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "test-destination",
                },
            ]
        }
        mock_api_client.get.return_value = mock_response

        result = destinations.fetch(name="test-destination")

        assert str(result.id) == "123e4567-e89b-12d3-a456-426655440000"
        destinations.logger.warning.assert_called_once()
