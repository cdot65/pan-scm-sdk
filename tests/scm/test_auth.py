# tests/scm/test_auth.py
import logging

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
