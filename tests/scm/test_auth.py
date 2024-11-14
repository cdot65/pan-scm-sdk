# tests/scm/test_auth.py
import base64
import json
import logging

import jwt
import pytest
from unittest.mock import patch, MagicMock
from scm.auth import OAuth2Client
from scm.models.auth import AuthRequestModel
from scm.exceptions import APIError
from jwt.exceptions import ExpiredSignatureError
from pydantic import ValidationError as PydanticValidationError


class TestAuthBase:
    """Base class for Auth tests."""

    @pytest.fixture
    def auth_request(self):
        """Fixture for auth request model."""
        return AuthRequestModel(
            client_id="test_client_id",
            client_secret="test_client_secret",
            tsg_id="test_tsg_id",
        )

    @pytest.fixture
    def base64url_encode(self):
        """Fixture for base64url encoding function."""

        def _encode(data):
            if isinstance(data, dict):
                data = json.dumps(data).encode()
            elif isinstance(data, str):
                data = data.encode()

            padding_removed = base64.b64encode(data).rstrip(b"=")
            return (
                padding_removed.replace(b"+", b"-").replace(b"/", b"_").decode("ascii")
            )

        return _encode

    @pytest.fixture
    def create_test_jwt(self):
        def _create_jwt(kid="test_kid", payload=None):
            header = {"alg": "RS256", "kid": kid}
            payload = payload or {"aud": "test_client_id", "exp": 1735689600}

            def base64url_encode(data):
                return (
                    base64.urlsafe_b64encode(json.dumps(data).encode())
                    .rstrip(b"=")
                    .decode("utf-8")
                )

            return f"{base64url_encode(header)}.{base64url_encode(payload)}.signature"

        return _create_jwt

    @pytest.fixture
    def mock_valid_token(self, create_test_jwt):
        return {"access_token": create_test_jwt()}

    @pytest.fixture(autouse=True)
    def mock_logger(self):
        """Mock logger for testing."""
        mock_log = MagicMock(
            spec=logging.Logger
        )  # This ensures it has all logger methods
        mock_log.error = MagicMock()
        mock_log.debug = MagicMock()
        mock_log.info = MagicMock()

        with patch("scm.auth.logger", mock_log):
            yield mock_log

    @pytest.fixture(autouse=True)
    def setup_method(
        self,
        auth_request,
    ):
        """Setup method that runs before each test."""

        # Mock the fetch_token method to set self.session.token
        def mock_fetch_token(
            *args,
            **kwargs,
        ):
            # Note: Since self.client is not yet instantiated, we need to set self.session.token after instantiation
            return {"access_token": "test_access_token"}

        with patch(
            "requests_oauthlib.OAuth2Session.fetch_token",
            side_effect=mock_fetch_token,
        ):
            # Mock _get_signing_key to return a mock signing key
            with patch.object(
                OAuth2Client,
                "_get_signing_key",
                return_value=MagicMock(key="mocked_key"),
            ):
                self.client = OAuth2Client(auth_request)
                # Set self.session.token after self.client is created
                self.client.session.token = {"access_token": "test_access_token"}

    @pytest.fixture
    def mock_token(self):
        """Fixture for test JWT token."""
        return {
            "access_token": "test.token.string",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    @pytest.fixture
    def mock_jwks_client(self):
        """Fixture for JWKS client."""
        with patch("jwt.PyJWKClient") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance


class TestAuthModelValidation(TestAuthBase):
    """Tests for Auth model validation."""

    def test_auth_request_model_with_scope(
        self,
        auth_request,
    ):
        """Test AuthRequestModel when scope is explicitly provided."""
        auth_request.scope = "custom_scope"
        assert auth_request.scope == "custom_scope"
        assert auth_request.tsg_id == "test_tsg_id"

    def test_auth_request_model_scope_construction(self):
        """Test automatic scope construction when scope is not provided."""
        auth_request = AuthRequestModel(
            client_id="test_client_id",
            client_secret="test_client_secret",
            tsg_id="test_tsg_id",
        )
        assert auth_request.scope == "tsg_id:test_tsg_id"

    def test_auth_request_model_missing_tsg_id(self):
        """Test that ValidationError is raised when tsg_id is missing and scope is not provided."""
        with pytest.raises(PydanticValidationError) as exc_info:
            AuthRequestModel(
                client_id="test_client_id",
                client_secret="test_client_secret",
                tsg_id=None,
            )
        assert "1 validation error for AuthRequestModel" in str(exc_info.value)
        assert "Value error, tsg_id is required to construct scope" in str(
            exc_info.value
        )

    def test_auth_request_model_empty_scope(self):
        """Test handling of empty scope string."""
        with pytest.raises(ValueError):
            AuthRequestModel(
                client_id="test_client_id",
                client_secret="test_client_secret",
                tsg_id="test_tsg_id",
                scope="",
            )

    def test_auth_request_model_custom_token_url(self):
        """Test custom token URL validation."""
        custom_url = "https://custom.auth.url/token"
        auth_request = AuthRequestModel(
            client_id="test_client_id",
            client_secret="test_client_secret",
            tsg_id="test_tsg_id",
            token_url=custom_url,
        )
        assert auth_request.token_url == custom_url


class TestAuthTokenOperations(TestAuthBase):
    """Tests for token operations."""

    def test_decode_token_success(self):
        """Test successful token decoding."""
        with patch("jwt.decode", return_value={"some": "payload"}) as mock_jwt_decode:
            payload = self.client.decode_token()
            mock_jwt_decode.assert_called_once_with(
                self.client.session.token["access_token"],
                self.client.signing_key.key,
                algorithms=["RS256"],
                audience=self.client.auth_request.client_id,
            )
            assert payload == {"some": "payload"}

    def test_decode_token_expired(self):
        """Test handling expired token."""
        with patch("jwt.decode", side_effect=ExpiredSignatureError):
            with pytest.raises(ExpiredSignatureError):
                self.client.decode_token()

    def test_is_expired_false(self):
        """Test token expiration check when not expired."""
        with patch(
            "jwt.decode",
            return_value={"some": "payload"},
        ):
            assert not self.client.is_expired

    def test_is_expired_true(self):
        """Test token expiration check when expired."""
        with patch(
            "jwt.decode",
            side_effect=ExpiredSignatureError,
        ):
            assert self.client.is_expired


class TestAuthTokenRefresh(TestAuthBase):
    """Tests for token refresh operations."""

    def test_refresh_token_success(self):
        """Test successful token refresh."""
        new_token = {"access_token": "new_access_token"}

        def mock_fetch_token(*args, **kwargs):
            self.client.session.token = new_token
            return new_token

        with patch.object(
            self.client.session,
            "fetch_token",
            side_effect=mock_fetch_token,
        ) as mock_fetch_token_method, patch.object(
            self.client,
            "_get_signing_key",
            return_value=MagicMock(key="mocked_key"),
        ) as mock_get_signing_key:
            self.client.refresh_token()

            mock_fetch_token_method.assert_called_once_with(
                token_url=self.client.auth_request.token_url,
                client_id=self.client.auth_request.client_id,
                client_secret=self.client.auth_request.client_secret,
                scope=self.client.auth_request.scope,
                include_client_id=True,
                client_kwargs={"tsg_id": self.client.auth_request.tsg_id},
            )
            mock_get_signing_key.assert_called_once()
            assert self.client.session.token["access_token"] == "new_access_token"

    def test_refresh_token_exception(self):
        """Test error handling during token refresh."""
        with patch.object(
            self.client.session,
            "fetch_token",
            side_effect=Exception("Network Error"),
        ):
            with pytest.raises(APIError) as exc_info:
                self.client.refresh_token()
            assert "Failed to refresh token: Network Error" in str(exc_info.value)

    def test_refresh_token_timeout(self):
        """Test token refresh with network timeout."""
        with patch.object(
            self.client.session,
            "fetch_token",
            side_effect=TimeoutError("Connection timed out"),
        ):
            with pytest.raises(APIError) as exc_info:
                self.client.refresh_token()
            assert "Connection timed out" in str(exc_info.value)

    def test_decode_token_invalid_format(self):
        """Test handling of malformed JWT tokens."""
        self.client.session.token["access_token"] = "invalid.token.format"
        with pytest.raises(jwt.InvalidTokenError):
            self.client.decode_token()


def _generate_dummy_jwt():
    """Generate a dummy JWT token for testing purposes."""
    header = {"alg": "RS256", "kid": "test_kid"}
    payload = {"some": "payload"}

    def base64url_encode(data):
        return base64.urlsafe_b64encode(data).rstrip(b"=")

    header_b64 = base64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = base64url_encode(json.dumps(payload).encode("utf-8"))
    signature_b64 = base64url_encode(b"signature")

    test_token = b".".join([header_b64, payload_b64, signature_b64]).decode("utf-8")
    return test_token


class TestGetSigningKey(TestAuthBase):
    """Tests for the _get_signing_key method of OAuth2Client."""

    def test_get_signing_key_success(self, auth_request):
        """Test that _get_signing_key retrieves the signing key successfully."""

        def base64url_encode(data):
            if isinstance(data, dict):
                data = json.dumps(data).encode()
            elif isinstance(data, str):
                data = data.encode()
            padding_removed = base64.b64encode(data).rstrip(b"=")
            return (
                padding_removed.replace(b"+", b"-").replace(b"/", b"_").decode("ascii")
            )

        header = {"alg": "RS256", "kid": "test_kid"}
        payload = {"aud": "test_client_id", "exp": 1735689600}

        test_token = (
            f"{base64url_encode(header)}."
            f"{base64url_encode(payload)}."
            f"{base64url_encode('signature')}"
        )

        # Mock the JWKS response
        mock_jwks_response = {
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "test_modulus",
                    "e": "AQAB",
                }
            ]
        }

        with patch("scm.auth.OAuth2Session") as mock_oauth2session, patch(
            "urllib.request.urlopen"
        ) as mock_urlopen:
            # Mock the URL fetch response
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(mock_jwks_response).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_response

            # Create mock session
            mock_session = MagicMock()
            mock_session.token = {"access_token": test_token}
            mock_session.fetch_token.return_value = {"access_token": test_token}
            mock_oauth2session.return_value = mock_session

            client = OAuth2Client(auth_request)
            assert client.signing_key is not None

    def test_get_signing_key_exception(self, auth_request):
        """Test that _get_signing_key handles exceptions properly."""

        # Generate a dummy valid JWT token
        test_token = _generate_dummy_jwt()

        # Mock the OAuth2Session to ensure 'token' attribute is set correctly
        with patch("scm.auth.OAuth2Session") as mock_oauth2session, patch(
            "jwt.PyJWKClient"
        ) as mock_pyjwkclient, patch("scm.auth.logger") as mock_logger:
            # Create a mock OAuth2Session instance
            mock_session = MagicMock()
            mock_session.token = {"access_token": test_token}
            mock_oauth2session.return_value = mock_session

            # Mock the fetch_token method to set the token on the session
            mock_session.fetch_token.return_value = {"access_token": test_token}

            # Create a mock instance of PyJWKClient
            mock_jwks_client = MagicMock()
            mock_pyjwkclient.return_value = mock_jwks_client

            # Mock get_signing_key_from_jwt to raise an exception
            mock_jwks_client.get_signing_key_from_jwt.side_effect = Exception(
                "Key error"
            )

            # Now instantiate the client; this should call _get_signing_key and raise an exception
            with pytest.raises(Exception) as exc_info:
                OAuth2Client(auth_request)

            # Check that the exception message is as expected
            assert "Unable to find a signing key that matches: " in str(exc_info.value)

            # Ensure that logger.error was called
            # mock_logger.error.assert_called()

    def test_get_signing_key_url_construction(self):
        """Test JWKS URI construction."""
        base_url = "https://custom.auth.url/oauth2"
        self.client.auth_request.token_url = f"{base_url}/access_token"

        def base64url_encode(data):
            if isinstance(data, dict):
                data = json.dumps(data).encode()
            elif isinstance(data, str):
                data = data.encode()
            padding_removed = base64.b64encode(data).rstrip(b"=")
            return (
                padding_removed.replace(b"+", b"-").replace(b"/", b"_").decode("ascii")
            )

        header = {"alg": "RS256", "kid": "test_kid"}
        payload = {"aud": "test_client_id", "exp": 1735689600}

        test_token = (
            f"{base64url_encode(header)}."
            f"{base64url_encode(payload)}."
            f"{base64url_encode('signature')}"
        )

        # Mock the JWKS response
        mock_jwks_response = {
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "test_modulus",
                    "e": "AQAB",
                }
            ]
        }

        # Update the session token
        self.client.session.token = {"access_token": test_token}

        with patch("urllib.request.urlopen") as mock_urlopen:
            # Mock the URL fetch response
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(mock_jwks_response).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_response

            self.client._get_signing_key()

            # Verify the URL construction
            called_url = mock_urlopen.call_args[0][0].full_url
            assert called_url == f"{base_url}/connect/jwk_uri"


class TestOAuth2Client(TestAuthBase):
    def test_create_session_error(self):
        """Test error handling during session creation."""
        with patch(
            "requests_oauthlib.OAuth2Session.fetch_token",
            side_effect=Exception("Failed to create session"),
        ):
            with patch.object(
                OAuth2Client, "_get_signing_key"
            ):  # Prevent _get_signing_key from being called
                with pytest.raises(APIError) as exc_info:
                    oauth_client = OAuth2Client(self.auth_request)
                assert "Failed to create session" in str(exc_info.value)
