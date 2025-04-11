# tests/test_auth.py

# Standard library imports
import time
from unittest.mock import MagicMock, patch

# External libraries
import pytest
from jwt.exceptions import ExpiredSignatureError, PyJWKClientError
from requests.exceptions import HTTPError, RequestException, Timeout

# Local SDK imports
from scm.auth import OAuth2Client
from scm.exceptions import APIError
from scm.models.auth import AuthRequestModel
from tests.utils import raise_mock_http_error


@pytest.fixture
def auth_request():
    """Create a mock auth request object."""
    return AuthRequestModel(
        client_id="test_client_id",
        client_secret="test_client_secret",
        token_url="https://api.test.com/oauth2/token",
        scope="test_scope",
        tsg_id="test_tsg_id",
    )


@pytest.mark.usefixtures("load_env")
class TestOAuth2Client:
    """Test suite for OAuth2Client."""

    @pytest.fixture(autouse=True)
    def setup(self, auth_request):
        """Setup test fixtures."""
        # Mock token response
        self.mock_token = {
            "access_token": "mock_token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        # Mock JWT payload
        self.mock_jwt_payload = {
            "aud": "test_client_id",
            "exp": 1735689600,  # Far future timestamp
            "sub": "test_subject",
        }

        # Create patches
        self.mock_oauth_session = patch("scm.auth.OAuth2Session").start()
        self.mock_jwks_client = patch("scm.auth.PyJWKClient").start()
        self.mock_jwt = patch("scm.auth.jwt").start()

        # Configure mocks
        self.mock_session = MagicMock()
        self.mock_session.token = self.mock_token
        self.mock_oauth_session.return_value = self.mock_session

        self.mock_signing_key = MagicMock()
        self.mock_signing_key.key = "mock_key"
        self.mock_jwks_client_instance = MagicMock()
        self.mock_jwks_client_instance.get_signing_key_from_jwt.return_value = self.mock_signing_key
        self.mock_jwks_client.return_value = self.mock_jwks_client_instance

        self.mock_jwt.decode.return_value = self.mock_jwt_payload

        yield

        # Clean up patches
        patch.stopall()

    def test_create_session_success(self, auth_request):
        """Test successful session creation."""
        OAuth2Client(auth_request)

        self.mock_oauth_session.assert_called_once()
        self.mock_session.fetch_token.assert_called_once_with(
            token_url=auth_request.token_url,
            client_id=auth_request.client_id,
            client_secret=auth_request.client_secret,
            scope=auth_request.scope,
            timeout=30,
            include_client_id=True,
            client_kwargs={"tsg_id": auth_request.tsg_id},
        )

    def test_get_signing_key_no_token(self, auth_request):
        """Test signing key retrieval with no token available."""
        # Set up a session with no token
        self.mock_session.token = None

        # Instantiate client and inject mock session without token
        client = OAuth2Client(auth_request)
        client.session = self.mock_session

        # Expect APIError when trying to get signing key without token
        with pytest.raises(APIError):
            client._get_signing_key()

    def test_token_expires_soon_with_expiry(self, auth_request):
        """Test token expiration check that returns True when token is about to expire."""
        # Set the token's expiration time in the near future (5 minutes from now)
        future_time = time.time() + 120  # 2 minutes in the future
        self.mock_token["expires_at"] = future_time
        self.mock_session.token = self.mock_token

        # Instantiate client and inject mock session
        client = OAuth2Client(auth_request)
        client.session = self.mock_session

        # Since the token expiry time is in less than the buffer time (5 minutes), token_expires_soon should return True
        assert client.token_expires_soon

    def test_create_session_general_error(self, auth_request):
        """Test session creation with general error."""
        self.mock_session.fetch_token.side_effect = Exception("Test error")

        with pytest.raises(APIError):
            OAuth2Client(auth_request)

    def test_get_signing_key_success(self, auth_request):
        """Test successful signing key retrieval."""
        client = OAuth2Client(auth_request)

        expected_jwks_uri = "https://api.test.com/oauth2/connect/jwk_uri"
        self.mock_jwks_client.assert_called_once_with(expected_jwks_uri)
        self.mock_jwks_client_instance.get_signing_key_from_jwt.assert_called_once_with(
            "mock_token"
        )
        assert client.signing_key == self.mock_signing_key

    def test_get_signing_key_error(self, auth_request):
        """Test signing key retrieval error."""
        self.mock_jwks_client_instance.get_signing_key_from_jwt.side_effect = PyJWKClientError(
            "Test error"
        )

        with pytest.raises(APIError):
            OAuth2Client(auth_request)

    def test_decode_token_success(self, auth_request):
        """Test successful token decoding."""
        client = OAuth2Client(auth_request)
        payload = client.decode_token()

        self.mock_jwt.decode.assert_called_with(
            "mock_token",
            self.mock_signing_key.key,
            algorithms=["RS256"],
            audience="test_client_id",
        )
        assert payload == self.mock_jwt_payload

    def test_decode_token_expired(self, auth_request):
        """Test token decoding with expired token."""
        self.mock_jwt.decode.side_effect = ExpiredSignatureError()
        client = OAuth2Client(auth_request)

        with pytest.raises(ExpiredSignatureError):
            client.decode_token()

    def test_decode_token_error(self, auth_request):
        """Test token decoding with general error."""
        self.mock_jwt.decode.side_effect = Exception("Test error")
        client = OAuth2Client(auth_request)

        with pytest.raises(APIError):
            client.decode_token()

    def test_is_expired_false(self, auth_request):
        """Test token expiration check when not expired."""
        client = OAuth2Client(auth_request)
        assert not client.is_expired

    def test_is_expired_true(self, auth_request):
        """Test token expiration check when expired."""
        self.mock_jwt.decode.side_effect = ExpiredSignatureError()
        client = OAuth2Client(auth_request)
        assert client.is_expired

    def test_is_expired_error(self, auth_request):
        """Test token expiration check with error."""
        self.mock_jwt.decode.side_effect = Exception("Test error")
        client = OAuth2Client(auth_request)

        with pytest.raises(APIError):
            _ = client.is_expired

    def test_refresh_token_success(self, auth_request):
        """Test successful token refresh."""
        client = OAuth2Client(auth_request)
        client.refresh_token()

        self.mock_session.fetch_token.assert_called_with(
            token_url=auth_request.token_url,
            client_id=auth_request.client_id,
            client_secret=auth_request.client_secret,
            scope=auth_request.scope,
            timeout=30,
            verify=True,
            include_client_id=True,
            client_kwargs={"tsg_id": auth_request.tsg_id},
        )

    def test_refresh_token_http_error(self, auth_request):
        """Test token refresh with HTTP error."""
        client = OAuth2Client(auth_request)
        self.mock_session.fetch_token.side_effect = raise_mock_http_error(
            status_code=401,
            error_code="E016",
            message="Invalid credentials",
            error_type="Invalid Credential",
        )

        with pytest.raises(APIError) as exc_info:
            client.refresh_token()

        assert "{'errorType': 'Invalid Credential'} - HTTP error: 401 - API error: E016" in str(
            exc_info.value
        )

    def test_refresh_token_general_error(self, auth_request):
        """Test token refresh with general error."""
        client = OAuth2Client(auth_request)
        self.mock_session.fetch_token.side_effect = Exception("Test error")

        with pytest.raises(APIError):
            client.refresh_token()

    def test_refresh_token_http_error_no_content(self, auth_request):
        """Test token refresh with HTTP error but no content."""
        client = OAuth2Client(auth_request)
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_session.fetch_token.side_effect = HTTPError(response=mock_response)

        with pytest.raises(APIError):
            client.refresh_token()

    def test_create_session_network_error(self, auth_request):
        """Test session creation with network error."""
        self.mock_session.fetch_token.side_effect = Timeout("Test timeout error")

        with pytest.raises(APIError):
            OAuth2Client(auth_request)

    # def test_create_session_http_error(self, auth_request):
    #     """Test session creation with HTTP error."""
    #     # Simulate an HTTPError during token fetching
    #     self.mock_session.fetch_token.side_effect = raise_mock_http_error(
    #         status_code=401,
    #         error_code="E016",
    #         message="{'errorType': 'Invalid Credential'} - HTTP error: 401 - API error: E016",
    #         error_type="Invalid Credential",
    #     )
    #
    #     with pytest.raises(APIError) as exc_info:
    #         OAuth2Client(auth_request)
    #
    #     # Check if APIError was raised with the expected message
    #     assert (
    #         "{'errorType': 'Invalid Credential'} - HTTP error: 401 - API error: E016"
    #         in str(exc_info.value)
    #     )

    def test_token_expires_soon_no_token(self, auth_request):
        """Test token expiration check with no token available."""
        self.mock_session.token = None
        client = OAuth2Client(auth_request)
        client.session = self.mock_session

        assert client.token_expires_soon

    def test_is_expired_no_token(self, auth_request):
        """Test token expiration check with no token, expect True."""
        self.mock_session.token = None
        client = OAuth2Client(auth_request)
        client.session = self.mock_session

        assert client.is_expired

    def test_refresh_token_network_error(self, auth_request):
        """Test token refresh with network error."""
        client = OAuth2Client(auth_request)
        self.mock_session.fetch_token.side_effect = Timeout("Timeout during refresh")

        with pytest.raises(APIError):
            client.refresh_token()

    def test_refresh_token_request_exception(self, auth_request):
        """Test token refresh with general request error."""
        client = OAuth2Client(auth_request)
        self.mock_session.fetch_token.side_effect = RequestException(
            "Request failed during refresh"
        )

        with pytest.raises(APIError):
            client.refresh_token()

    def test_create_session_http_error(self, auth_request):
        """Test session creation with HTTP error."""
        # Create mock HTTP error response with correct error format
        mock_response = MagicMock()
        mock_response.content = b'{"error": "test_error"}'
        mock_response.content = b'{"_errors": [{"code": "E001", "message": "HTTP Error"}]}'
        mock_response.json.return_value = {"_errors": [{"code": "E001", "message": "HTTP Error"}]}
        mock_response.status_code = 500

        # Create HTTPError with mock response
        http_error = HTTPError("Test HTTP Error")
        http_error.response = mock_response

        # Patch OAuth2Session to raise the HTTP error
        self.mock_session.fetch_token.side_effect = http_error

        # Assert APIError is raised with expected message
        with pytest.raises(APIError) as exc_info:
            OAuth2Client(auth_request)

        assert "HTTP error: 500 - API error: E001" in str(exc_info.value)
