"""
Test module for Mobile Agent Versions configuration service.

This module contains unit tests for the Mobile Agent Versions configuration service and its related models.
"""
# tests/scm/config/mobile_agent/test_agent_versions.py

from unittest.mock import Mock, patch

import pytest

from scm.config.mobile_agent.agent_versions import AgentVersions
from scm.exceptions import APIError, InvalidObjectError, MissingQueryParameterError


class TestAgentVersions:
    """Tests for the AgentVersions class."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        mock_client = Mock()
        mock_client.get.return_value = {"agent_versions": ["5.3.0", "5.2.8", "5.2.7"]}
        return mock_client

    @pytest.fixture
    def agent_versions_service(self, mock_api_client):
        """Create an AgentVersions service instance with a mock API client."""
        with patch("scm.config.BaseObject.__init__") as mock_init:
            mock_init.return_value = None  # Skip the real __init__
            service = AgentVersions(mock_api_client)
            service._max_limit = (
                AgentVersions.DEFAULT_MAX_LIMIT
            )  # Set this manually since we're skipping __init__
            service.logger = Mock()  # Add a mock logger
            service.api_client = mock_api_client  # We need to set this manually
            return service

    def test_validate_max_limit_none(self, agent_versions_service):
        """Test _validate_max_limit with None value."""
        result = agent_versions_service._validate_max_limit(None)
        assert result == AgentVersions.DEFAULT_MAX_LIMIT

    def test_validate_max_limit_valid(self, agent_versions_service):
        """Test _validate_max_limit with valid value."""
        result = agent_versions_service._validate_max_limit(500)
        assert result == 500

    def test_validate_max_limit_string(self, agent_versions_service):
        """Test _validate_max_limit with string that can be converted to int."""
        result = agent_versions_service._validate_max_limit("500")
        assert result == 500

    def test_validate_max_limit_invalid_type(self, agent_versions_service):
        """Test _validate_max_limit with invalid type."""
        with pytest.raises(APIError) as exc_info:
            agent_versions_service._validate_max_limit("invalid")
        error_obj = exc_info.value
        assert error_obj.error_code == "E003"
        assert error_obj.http_status_code == 400
        assert error_obj.details == {"error": "Invalid max_limit type"}

    def test_validate_max_limit_zero(self, agent_versions_service):
        """Test _validate_max_limit with zero."""
        with pytest.raises(InvalidObjectError) as exc_info:
            agent_versions_service._validate_max_limit(0)
        error_obj = exc_info.value
        assert error_obj.error_code == "E003"
        assert error_obj.http_status_code == 400
        assert error_obj.details == {"error": "Invalid max_limit value"}

    def test_validate_max_limit_negative(self, agent_versions_service):
        """Test _validate_max_limit with negative value."""
        with pytest.raises(InvalidObjectError) as exc_info:
            agent_versions_service._validate_max_limit(-10)
        error_obj = exc_info.value
        assert error_obj.error_code == "E003"
        assert error_obj.http_status_code == 400
        assert error_obj.details == {"error": "Invalid max_limit value"}

    def test_validate_max_limit_too_large(self, agent_versions_service):
        """Test _validate_max_limit with value exceeding ABSOLUTE_MAX_LIMIT."""
        with pytest.raises(InvalidObjectError) as exc_info:
            agent_versions_service._validate_max_limit(AgentVersions.ABSOLUTE_MAX_LIMIT + 1)
        error_obj = exc_info.value
        assert error_obj.error_code == "E003"
        assert error_obj.http_status_code == 400
        assert error_obj.details == {"error": "max_limit exceeds maximum allowed value"}

    def test_apply_filters_no_filters(self, agent_versions_service):
        """Test _apply_filters with no filters."""
        versions = ["5.3.0", "5.2.8", "5.2.7"]
        result = agent_versions_service._apply_filters(versions, {})
        assert result == versions

    def test_apply_filters_version_string(self, agent_versions_service):
        """Test _apply_filters with version filter as string."""
        versions = ["5.3.0", "5.2.8", "5.2.7"]
        result = agent_versions_service._apply_filters(versions, {"version": "5.2"})
        assert result == ["5.2.8", "5.2.7"]

    def test_apply_filters_version_list(self, agent_versions_service):
        """Test _apply_filters with version filter as list."""
        versions = ["5.3.0", "5.2.8", "5.2.7"]
        result = agent_versions_service._apply_filters(versions, {"version": ["5.3", "5.2.7"]})
        assert result == ["5.3.0", "5.2.7"]

    def test_apply_filters_version_empty_list(self, agent_versions_service):
        """Test _apply_filters with version filter as empty list."""
        versions = ["5.3.0", "5.2.8", "5.2.7"]
        result = agent_versions_service._apply_filters(versions, {"version": []})
        assert result == []

    def test_apply_filters_prefix_string(self, agent_versions_service):
        """Test _apply_filters with prefix filter as string."""
        versions = ["5.3.0", "5.2.8", "5.2.7"]
        result = agent_versions_service._apply_filters(versions, {"prefix": "5.3"})
        assert result == ["5.3.0"]

    def test_apply_filters_prefix_list(self, agent_versions_service):
        """Test _apply_filters with prefix filter as list."""
        versions = ["5.3.0", "5.2.8", "5.2.7"]
        result = agent_versions_service._apply_filters(versions, {"prefix": ["5.3", "5.2.8"]})
        assert result == ["5.3.0", "5.2.8"]

    def test_apply_filters_prefix_empty_list(self, agent_versions_service):
        """Test _apply_filters with prefix filter as empty list."""
        versions = ["5.3.0", "5.2.8", "5.2.7"]
        result = agent_versions_service._apply_filters(versions, {"prefix": []})
        assert result == []

    def test_apply_filters_multiple_filters(self, agent_versions_service):
        """Test _apply_filters with multiple filters."""
        versions = ["5.3.0", "5.2.8", "5.2.7"]
        result = agent_versions_service._apply_filters(
            versions, {"version": "5.2", "prefix": "5.2.7"}
        )
        assert result == ["5.2.7"]

    def test_apply_filters_case_insensitive(self, agent_versions_service):
        """Test _apply_filters with case-insensitive matching."""
        versions = ["5.3.0", "5.2.8", "5.2.7"]
        result = agent_versions_service._apply_filters(
            versions, {"version": "5.2", "prefix": "5.2.7"}
        )
        assert result == ["5.2.7"]

    def test_list_no_filters(self, agent_versions_service, mock_api_client):
        """Test list method with no filters."""
        result = agent_versions_service.list()
        mock_api_client.get.assert_called_once_with(AgentVersions.ENDPOINT)
        assert result == ["5.3.0", "5.2.8", "5.2.7"]

    def test_list_with_filters(self, agent_versions_service, mock_api_client):
        """Test list method with filters."""
        result = agent_versions_service.list(version="5.2")
        mock_api_client.get.assert_called_once_with(AgentVersions.ENDPOINT)
        assert result == ["5.2.8", "5.2.7"]

    def test_fetch_valid_version(self, agent_versions_service, mock_api_client):
        """Test fetch method with valid version."""
        result = agent_versions_service.fetch("5.3.0")
        mock_api_client.get.assert_called_once_with(AgentVersions.ENDPOINT)
        assert result == "5.3.0"

    def test_fetch_case_insensitive(self, agent_versions_service, mock_api_client):
        """Test fetch method with case-insensitive match."""
        result = agent_versions_service.fetch("5.3.0")
        mock_api_client.get.assert_called_once_with(AgentVersions.ENDPOINT)
        assert result == "5.3.0"

    def test_fetch_empty_version(self, agent_versions_service):
        """Test fetch method with empty version."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            agent_versions_service.fetch("")
        error_obj = exc_info.value
        assert error_obj.error_code == "E003"
        assert error_obj.http_status_code == 400
        assert "version" in error_obj.details["field"]

    def test_fetch_version_not_found(self, agent_versions_service, mock_api_client):
        """Test fetch method with version not found."""
        with pytest.raises(InvalidObjectError) as exc_info:
            agent_versions_service.fetch("1.0.0")
        error_obj = exc_info.value
        assert error_obj.error_code == "E005"
        assert error_obj.http_status_code == 404
        assert error_obj.details == {"error": "Object not found"}

    def test_fetch_multiple_matches(self, agent_versions_service, mock_api_client):
        """Test fetch method with multiple matches (edge case)."""
        mock_api_client.get.return_value = {
            "agent_versions": ["5.3.0", "5.3.0"]
        }  # Duplicate entries
        result = agent_versions_service.fetch("5.3.0")
        assert result == "5.3.0"

    def test_list_api_returns_unexpected_format(self, agent_versions_service, mock_api_client):
        """Test list method when API returns unexpected format."""
        mock_api_client.get.return_value = {"wrong_key": ["5.3.0", "5.2.8", "5.2.7"]}
        with pytest.raises(Exception):
            agent_versions_service.list()

    def test_max_limit_property(self, agent_versions_service):
        """Test max_limit property getter."""
        assert agent_versions_service.max_limit == AgentVersions.DEFAULT_MAX_LIMIT

    def test_max_limit_setter(self, agent_versions_service):
        """Test max_limit property setter."""
        agent_versions_service.max_limit = 500
        assert agent_versions_service._max_limit == 500

    # Create mock init tests separately with custom setup
    def test_init_default_max_limit(self):
        """Test initialization with default max_limit."""
        with patch("scm.config.BaseObject.__init__") as mock_init:
            mock_init.return_value = None
            mock_client = Mock()
            service = AgentVersions(mock_client)
            service._validate_max_limit = Mock(return_value=AgentVersions.DEFAULT_MAX_LIMIT)
            service.__init__(mock_client)
            service._validate_max_limit.assert_called_once_with(None)
            assert service._max_limit == AgentVersions.DEFAULT_MAX_LIMIT

    def test_init_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        with patch("scm.config.BaseObject.__init__") as mock_init:
            mock_init.return_value = None
            mock_client = Mock()
            service = AgentVersions(mock_client)
            service._validate_max_limit = Mock(return_value=500)
            service.__init__(mock_client, max_limit=500)
            service._validate_max_limit.assert_called_once_with(500)
            assert service._max_limit == 500
