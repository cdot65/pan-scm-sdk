"""Test module for Forwarding Profile Regional and Custom Proxies configuration service.

This module contains unit tests for the Regional and Custom Proxies configuration service.
"""
# tests/scm/config/mobile_agent/test_forwarding_profile_regional_and_custom_proxies.py

from unittest.mock import MagicMock, patch

import pytest

from scm.config.mobile_agent import ForwardingProfileRegionalAndCustomProxies
from scm.exceptions import (
    APIError,
    InvalidObjectError,
    MissingQueryParameterError,
    ObjectNotPresentError,
)
from scm.models.mobile_agent import (
    ForwardingProfileRegionalAndCustomProxyResponseModel,
    ForwardingProfileRegionalAndCustomProxyUpdateModel,
)

TEST_ID = "123e4567-e89b-12d3-a456-426655440000"


def sample_data():
    """Return a valid create payload for a regional and custom proxy."""
    return {
        "name": "emea-proxy",
        "type": "gp-and-pac",
        "description": "EMEA regional proxy",
        "proxy_1": {"fqdn": "proxy1.example.com", "port": 8080},
        "fallback_option": "fail-open",
    }


def sample_response(name=None):
    """Return a valid API response for a regional and custom proxy."""
    data = sample_data()
    if name is not None:
        data["name"] = name
    data["id"] = TEST_ID
    return data


class TestForwardingProfileRegionalAndCustomProxies:
    """Test cases for the ForwardingProfileRegionalAndCustomProxies service."""

    @pytest.fixture
    def mock_api_client(self):
        """Test fixture for mock API client."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_api_client):
        """Test fixture for ForwardingProfileRegionalAndCustomProxies instance."""
        with patch("scm.config.isinstance", return_value=True):
            svc = ForwardingProfileRegionalAndCustomProxies(mock_api_client)
            svc.logger = MagicMock()
            return svc

    def test_init_with_default_max_limit(self, mock_api_client):
        """Test initialization with default max limit value."""
        with patch("scm.config.isinstance", return_value=True):
            svc = ForwardingProfileRegionalAndCustomProxies(mock_api_client)
            assert svc._max_limit == ForwardingProfileRegionalAndCustomProxies.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_api_client):
        """Test initialization with custom max limit."""
        with patch("scm.config.isinstance", return_value=True):
            svc = ForwardingProfileRegionalAndCustomProxies(mock_api_client, max_limit=1000)
            assert svc._max_limit == 1000

    def test_validate_max_limit_with_invalid_type(self, service):
        """Test validate_max_limit with invalid type."""
        with pytest.raises(InvalidObjectError) as excinfo:
            service._validate_max_limit("not_an_int")
        assert "Invalid max_limit type" in str(excinfo.value.details)

    def test_validate_max_limit_with_negative_value(self, service):
        """Test validate_max_limit with negative value."""
        with pytest.raises(InvalidObjectError) as excinfo:
            service._validate_max_limit(-1)
        assert "Invalid max_limit value" in str(excinfo.value.details)

    def test_validate_max_limit_with_too_large_value(self, service):
        """Test validate_max_limit with value exceeding absolute max."""
        with pytest.raises(InvalidObjectError) as excinfo:
            service._validate_max_limit(ForwardingProfileRegionalAndCustomProxies.ABSOLUTE_MAX_LIMIT + 1)
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value.details)

    def test_validate_max_limit_with_valid_value(self, service):
        """Test validate_max_limit with valid value."""
        assert service._validate_max_limit(1000) == 1000

    def test_max_limit_property_getter(self, service):
        """Test max_limit property getter."""
        service._max_limit = 1000
        assert service.max_limit == 1000

    def test_max_limit_property_setter(self, service):
        """Test max_limit property setter."""
        service.max_limit = 1000
        assert service._max_limit == 1000

    def test_create(self, service, mock_api_client):
        """Test create method."""
        mock_api_client.post.return_value = sample_response()

        result = service.create(sample_data())

        assert isinstance(result, ForwardingProfileRegionalAndCustomProxyResponseModel)
        assert str(result.id) == TEST_ID

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == service.ENDPOINT
        assert call_args[1]["params"] == {"folder": "Mobile Users"}
        assert "json" in call_args[1]
        assert "id" not in call_args[1]["json"]

    def test_create_with_invalid_folder(self, service):
        """Test create method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            service.create(sample_data(), folder="Invalid")
        assert "Invalid folder value" in str(excinfo.value.details)

    def test_get(self, service, mock_api_client):
        """Test get method."""
        mock_api_client.get.return_value = sample_response()

        result = service.get(TEST_ID)

        assert isinstance(result, ForwardingProfileRegionalAndCustomProxyResponseModel)
        assert str(result.id) == TEST_ID
        mock_api_client.get.assert_called_once_with(f"{service.ENDPOINT}/{TEST_ID}")

    def test_get_not_found(self, service, mock_api_client):
        """Test get method when the object does not exist."""
        mock_api_client.get.side_effect = APIError(
            "Object not found",
            http_status_code=404,
        )

        with pytest.raises(ObjectNotPresentError):
            service.get(TEST_ID)

    def test_get_other_api_error_reraised(self, service, mock_api_client):
        """Test get method re-raises non-404 API errors."""
        mock_api_client.get.side_effect = APIError(
            "Server error",
            http_status_code=500,
        )

        with pytest.raises(APIError) as excinfo:
            service.get(TEST_ID)
        assert excinfo.value.http_status_code == 500

    def test_update(self, service, mock_api_client):
        """Test update method."""
        mock_api_client.put.return_value = sample_response()

        update_model = ForwardingProfileRegionalAndCustomProxyUpdateModel(id=TEST_ID, **sample_data())
        result = service.update(update_model)

        assert isinstance(result, ForwardingProfileRegionalAndCustomProxyResponseModel)
        mock_api_client.put.assert_called_once()
        call_args = mock_api_client.put.call_args
        assert call_args[0][0] == f"{service.ENDPOINT}/{TEST_ID}"
        assert "id" not in call_args[1]["json"]

    def test_delete(self, service, mock_api_client):
        """Test delete method."""
        service.delete(TEST_ID)

        mock_api_client.delete.assert_called_once_with(f"{service.ENDPOINT}/{TEST_ID}")

    def test_delete_not_found(self, service, mock_api_client):
        """Test delete method when the object does not exist."""
        mock_api_client.delete.side_effect = APIError(
            "Object not found",
            http_status_code=404,
        )

        with pytest.raises(ObjectNotPresentError):
            service.delete(TEST_ID)

    def test_list_with_dict_response(self, service, mock_api_client):
        """Test list method with dictionary response format."""
        mock_api_client.get.return_value = {
            "data": [sample_response("item-1"), sample_response("item-2")],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }

        result = service.list()

        assert len(result) == 2
        assert all(isinstance(item, ForwardingProfileRegionalAndCustomProxyResponseModel) for item in result)
        assert result[0].name == "item-1"
        assert result[1].name == "item-2"

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == service.ENDPOINT
        params = call_args[1]["params"]
        assert params["folder"] == "Mobile Users"
        assert params["limit"] == service.max_limit
        assert params["offset"] == 0

    def test_list_with_list_response(self, service, mock_api_client):
        """Test list method with a bare list response format."""
        mock_api_client.get.return_value = [sample_response("item-1")]

        result = service.list()

        assert len(result) == 1
        assert result[0].name == "item-1"

    def test_list_with_name_filter(self, service, mock_api_client):
        """Test list method passes the name filter server-side."""
        mock_api_client.get.return_value = {"data": [sample_response("item-1")]}

        service.list(name="item-1")

        params = mock_api_client.get.call_args[1]["params"]
        assert params["name"] == "item-1"

    def test_list_with_invalid_folder(self, service):
        """Test list method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            service.list(folder="Invalid")
        assert "Invalid folder value" in str(excinfo.value.details)

    def test_list_with_invalid_response(self, service, mock_api_client):
        """Test list method with invalid response structure."""
        mock_api_client.get.return_value = {"invalid": "response"}

        with pytest.raises(InvalidObjectError) as excinfo:
            service.list()
        assert "Response has invalid structure" in str(excinfo.value.details)

    def test_list_pagination(self, service, mock_api_client):
        """Test list method paginates until a partial page is returned."""
        service.max_limit = 1
        mock_api_client.get.side_effect = [
            {"data": [sample_response("item-1")]},
            {"data": []},
        ]

        result = service.list()

        assert len(result) == 1
        assert mock_api_client.get.call_count == 2

    def test_fetch_with_empty_name(self, service):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            service.fetch("")
        assert "name" in str(excinfo.value.details["field"])

    def test_fetch_with_invalid_folder(self, service):
        """Test fetch method with invalid folder."""
        with pytest.raises(InvalidObjectError) as excinfo:
            service.fetch("item-1", folder="Invalid")
        assert "Invalid folder value" in str(excinfo.value.details)

    def test_fetch_with_no_match(self, service, mock_api_client):
        """Test fetch method when no matching object is found."""
        mock_api_client.get.return_value = {"data": []}

        with pytest.raises(InvalidObjectError) as excinfo:
            service.fetch("non-existent")
        assert excinfo.value.http_status_code == 404

    def test_fetch_with_one_match(self, service, mock_api_client):
        """Test fetch method when one matching object is found."""
        mock_api_client.get.return_value = {"data": [sample_response("item-1")]}

        result = service.fetch("item-1")

        assert isinstance(result, ForwardingProfileRegionalAndCustomProxyResponseModel)
        assert result.name == "item-1"
        params = mock_api_client.get.call_args[1]["params"]
        assert params["name"] == "item-1"
        assert params["folder"] == "Mobile Users"

    def test_fetch_with_multiple_matches(self, service, mock_api_client):
        """Test fetch method returns the first of multiple matches."""
        mock_api_client.get.return_value = {
            "data": [sample_response("item-1"), sample_response("item-1")]
        }

        result = service.fetch("item-1")

        assert result.name == "item-1"
        service.logger.warning.assert_called_once()
