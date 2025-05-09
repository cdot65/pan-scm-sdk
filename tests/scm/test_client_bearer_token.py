# tests/scm/test_client_bearer_token.py
"""
Tests for bearer token authentication in the SCM client.

To be merged into test_client.py after the file structure is fixed.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from requests import Session

from scm.client import Scm, ScmClient
from scm.exceptions import APIError


class TestBearerTokenAuth:
    """Test cases for bearer token authentication."""

    def test_client_init_with_bearer_token(self):
        """Test that client initializes correctly with a bearer token."""
        token = "test_token_12345"
        client = Scm(access_token=token)

        # Verify oauth_client is None when using bearer token
        assert client.oauth_client is None

        # Verify session was created and has correct auth header
        assert client.session is not None
        assert isinstance(client.session, Session)
        assert client.session.headers["Authorization"] == f"Bearer {token}"

    def test_client_init_requires_credentials_or_token(self):
        """Test that client initialization requires either credentials or token."""
        # No credentials or token should raise error
        with pytest.raises(APIError):
            Scm()

        # Partial credentials should raise error
        with pytest.raises(APIError):
            Scm(client_id="test_id")

        with pytest.raises(APIError):
            Scm(client_id="test_id", client_secret="test_secret")

    def test_scm_client_alias_with_bearer_token(self):
        """Test that ScmClient alias works with bearer token."""
        token = "test_token_12345"
        client = ScmClient(access_token=token)

        # Verify oauth_client is None when using bearer token
        assert client.oauth_client is None

        # Verify session was created and has correct auth header
        assert client.session is not None
        assert isinstance(client.session, Session)
        assert client.session.headers["Authorization"] == f"Bearer {token}"

    @patch("requests.Session.request")
    def test_api_methods_skip_token_refresh(self, mock_request):
        """Test that API methods skip token refresh when using bearer token."""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = b'{"test": "response"}'
        mock_response.json.return_value = {"test": "response"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Initialize client with bearer token
        client = Scm(access_token="test_token")

        # Call API methods - no oauth_client means no refresh check should occur
        client.get("/test")
        client.post("/test")
        client.put("/test")
        client.delete("/test")

        # Verify request was called for each method
        assert mock_request.call_count == 4

    @patch("requests.Session.request")
    def test_commit_with_bearer_token(self, mock_request):
        """Test commit method requires admin when using bearer token."""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = (
            b'{"success": true, "job_id": "123", "message": "Commit job created"}'
        )
        mock_response.json.return_value = {
            "success": True,
            "job_id": "123",
            "message": "Commit job created",
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Initialize client with bearer token
        client = Scm(access_token="test_token")

        # Commit with no admin should raise error
        with pytest.raises(APIError) as exc_info:
            client.commit(folders=["test"], description="test commit")

        # Verify error message
        error = exc_info.value

        # Print the actual error message for debugging
        print(f"Error message: '{error.message}'")

        # Check for the exact error message
        expected_message = (
            "When using bearer token authentication, 'admin' must be provided for commit operations"
        )
        assert error.message == expected_message

        # Commit with admin should work
        response = client.commit(
            folders=["test"], description="test commit", admin=["test@example.com"]
        )

        assert response.success is True
        assert response.job_id == "123"

    @patch("requests.Session.request")
    def test_get_method_with_bearer_token(self, mock_request):
        """Test GET method with bearer token auth."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Create client with bearer token
        client = Scm(access_token="test_token")

        # Call get method
        response = client.get("/test-endpoint", params={"param1": "value1"})

        # Verify request was called with correct params
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert args[0] == "GET"
        assert "params" in kwargs
        assert kwargs["params"] == {"param1": "value1"}

        # Verify response was properly returned
        assert response == {"data": "test"}

    @patch("requests.Session.request")
    def test_dynamic_service_access_with_bearer_token(self, mock_request):
        """Test that dynamic service access works with bearer token."""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = b'{"data": []}'
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Initialize client with bearer token
        client = Scm(access_token="test_token")

        # Access a service dynamically
        address_service = client.address

        # Verify the service was created and properly initialized
        assert address_service is not None
        assert address_service.api_client == client
