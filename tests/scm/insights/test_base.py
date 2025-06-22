"""Test suite for InsightsBaseObject base class."""

from unittest.mock import Mock, patch

import pytest

from scm.insights import InsightsBaseObject


class ConcreteInsights(InsightsBaseObject):
    """Concrete implementation for testing the base class."""

    def get_resource_endpoint(self) -> str:
        """Return test resource endpoint."""
        return "resource/query/test_endpoint"


class TestInsightsBaseObject:
    """Tests for the InsightsBaseObject base class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock SCM client."""
        client = Mock()
        client.verify_ssl = True
        # Mock OAuth client
        client.oauth_client = Mock()
        client.oauth_client.session = Mock()
        client.oauth_client.session.token = {"access_token": "test-token"}
        client.oauth_client.auth_request = Mock()
        client.oauth_client.auth_request.tsg_id = "test-tsg-id"
        return client

    @pytest.fixture
    def mock_client_bearer(self):
        """Create a mock SCM client with bearer token auth."""
        client = Mock()
        client.verify_ssl = True
        # No OAuth client - using bearer token
        client.oauth_client = None
        client.session = Mock()
        client.session.headers = {"Authorization": "Bearer direct-token"}
        return client

    @pytest.fixture
    def insights_service(self, mock_client):
        """Create a concrete insights service instance."""
        return ConcreteInsights(mock_client)

    @pytest.fixture
    def insights_service_bearer(self, mock_client_bearer):
        """Create a concrete insights service with bearer auth."""
        return ConcreteInsights(mock_client_bearer)

    @patch("requests.post")
    def test_list_method(self, mock_post, insights_service):
        """Test the list convenience method."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 2,
                "requestId": "test-request",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [
                {"id": "item1", "name": "Test Item 1"},
                {"id": "item2", "name": "Test Item 2"},
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Call list method
        results = insights_service.list(max_results=50)

        # Verify request
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        # Check that count was set from max_results
        assert payload["count"] == 50

        # Verify results
        assert len(results) == 2
        assert results[0]["id"] == "item1"
        assert results[1]["id"] == "item2"

    @patch("requests.post")
    def test_list_with_existing_count(self, mock_post, insights_service):
        """Test list method when count is already in kwargs."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 1,
                "requestId": "test-request",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [{"id": "item1"}],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Call list with explicit count
        insights_service.list(count=25, max_results=100)

        # Verify count wasn't overridden
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["count"] == 25

    @patch("requests.post")
    def test_get_method(self, mock_post, insights_service):
        """Test the get method for retrieving specific resources."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 1,
                "requestId": "test-request",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [{"id": "test-123", "name": "Found Item"}],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Get specific resource
        result = insights_service.get("test-123")

        # Verify request tried common ID fields
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        # Should have filter for ID
        assert "filter" in payload
        assert payload["count"] == 1
        filter_rule = payload["filter"]["rules"][0]
        assert filter_rule["operator"] == "equals"
        assert filter_rule["values"] == ["test-123"]

        # Verify result
        assert result["id"] == "test-123"
        assert result["name"] == "Found Item"

    @patch("requests.post")
    def test_get_not_found(self, mock_post, insights_service):
        """Test get method when resource is not found."""
        # Mock empty response for all ID field attempts
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 0,
                "requestId": "test-request",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Should raise ValueError
        with pytest.raises(ValueError, match="Resource with ID 'nonexistent' not found"):
            insights_service.get("nonexistent")

        # Verify it tried multiple ID fields
        assert mock_post.call_count > 1

    @patch("requests.post")
    def test_bearer_token_auth(self, mock_post, insights_service_bearer):
        """Test authentication using bearer token instead of OAuth."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "header": {
                "createdAt": "2024-01-20T12:00:00Z",
                "dataCount": 0,
                "requestId": "test-request",
                "queryInput": {},
                "isResourceDataOverridden": False,
                "fieldList": [],
                "status": {"success": True},
                "name": "test",
            },
            "data": [],
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Make a query
        insights_service_bearer.query(count=10)

        # Verify bearer token was used
        call_args = mock_post.call_args
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer direct-token"
        assert "X-PANW-Region" in headers

    def test_prepare_headers_without_tsg_id(self, mock_client):
        """Test header preparation when TSG ID is not available."""
        # Remove TSG ID
        mock_client.oauth_client.auth_request.tsg_id = None

        service = ConcreteInsights(mock_client)
        headers = service._prepare_headers()

        # Should have region header but not prisma-tenant
        assert headers["X-PANW-Region"] == "americas"
        assert "prisma-tenant" not in headers

    def test_abstract_method_not_implemented(self):
        """Test that the abstract get_resource_endpoint must be implemented."""
        # This test ensures the abstract method coverage
        # The pass statement on line 34 is part of the abstract method definition
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            # Try to instantiate the abstract base class directly
            InsightsBaseObject(Mock())

    def test_abstract_method_definition(self):
        """Test the abstract method is properly defined."""
        # To cover line 34, we need to actually call the abstract method
        # We'll do this by calling it on the class itself (unbound)
        try:
            # This will execute the method body (including the pass statement)
            InsightsBaseObject.get_resource_endpoint(None)
        except AttributeError:
            # Expected since we're calling unbound method with None
            pass

        # Also verify it's properly marked as abstract
        method = InsightsBaseObject.get_resource_endpoint
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True
