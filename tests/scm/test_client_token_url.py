# tests/scm/test_client_token_url.py

from unittest.mock import MagicMock, patch

from scm.client import Scm, ScmClient
from scm.models.auth import AuthRequestModel


class TestClientTokenUrl:
    """Tests for custom token URL functionality in client."""

    @patch("scm.client.OAuth2Client")
    def test_custom_token_url(self, mock_oauth2client):
        """Test initialization with custom token URL."""
        # Configure the mock
        mock_oauth_client = mock_oauth2client.return_value
        mock_oauth_client.session = MagicMock()
        mock_oauth_client.is_expired = False
        mock_oauth_client.refresh_token = MagicMock()
        mock_oauth_client.signing_key = MagicMock(key="mocked_key")

        custom_token_url = "https://custom.auth.server.com/oauth2/token"

        # Create client with custom token_url
        Scm(
            client_id="test_client_id",
            client_secret="test_client_secret",
            tsg_id="test_tsg_id",
            token_url=custom_token_url,
        )

        # Verify the auth request was created with the custom token URL
        mock_oauth2client.assert_called_once()
        auth_request_arg = mock_oauth2client.call_args[0][0]
        assert isinstance(auth_request_arg, AuthRequestModel)
        assert auth_request_arg.token_url == custom_token_url

    @patch("scm.client.OAuth2Client")
    def test_default_token_url(self, mock_oauth2client):
        """Test initialization with default token URL."""
        # Configure the mock
        mock_oauth_client = mock_oauth2client.return_value
        mock_oauth_client.session = MagicMock()
        mock_oauth_client.is_expired = False
        mock_oauth_client.refresh_token = MagicMock()
        mock_oauth_client.signing_key = MagicMock(key="mocked_key")

        # Default token URL from AuthRequestModel
        default_token_url = "https://auth.apps.paloaltonetworks.com/am/oauth2/access_token"

        # Create client without specifying token_url
        Scm(client_id="test_client_id", client_secret="test_client_secret", tsg_id="test_tsg_id")

        # Verify the auth request was created with the default token URL
        auth_request_arg = mock_oauth2client.call_args[0][0]
        assert isinstance(auth_request_arg, AuthRequestModel)
        assert auth_request_arg.token_url == default_token_url

    @patch("scm.client.OAuth2Client")
    def test_scm_client_token_url(self, mock_oauth2client):
        """Test ScmClient alias with custom token URL."""
        # Configure the mock
        mock_oauth_client = mock_oauth2client.return_value
        mock_oauth_client.session = MagicMock()
        mock_oauth_client.is_expired = False
        mock_oauth_client.refresh_token = MagicMock()
        mock_oauth_client.signing_key = MagicMock(key="mocked_key")

        custom_token_url = "https://custom.auth.server.com/oauth2/token"

        # Create ScmClient with custom token_url
        ScmClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            tsg_id="test_tsg_id",
            token_url=custom_token_url,
        )

        # Verify the auth request was created with the custom token URL
        auth_request_arg = mock_oauth2client.call_args[0][0]
        assert isinstance(auth_request_arg, AuthRequestModel)
        assert auth_request_arg.token_url == custom_token_url
