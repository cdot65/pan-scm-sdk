# tests/scm/test_auth.py

import pytest
from unittest.mock import patch, MagicMock
from scm.auth import OAuth2Client
from scm.models.auth import AuthRequestModel
from jwt.exceptions import ExpiredSignatureError


# Sample AuthRequestModel for testing
@pytest.fixture
def auth_request():
    return AuthRequestModel(
        client_id="test_client_id",
        client_secret="test_client_secret",
        token_url="https://example.com/token",
        tsg_id="test_tsg_id",
    )


# Mocked OAuth2Session and PyJWKClient
@pytest.fixture
def oauth2client(auth_request):
    with patch("scm.auth.OAuth2Session") as MockOAuth2Session, patch(
        "scm.auth.PyJWKClient"
    ) as MockPyJWKClient:

        # Mock OAuth2Session
        mock_session = MockOAuth2Session.return_value

        # Mock fetch_token to return a sample token
        sample_token = {"access_token": "test_access_token"}
        mock_session.fetch_token.return_value = sample_token
        # Set session.token to the returned token
        mock_session.token = sample_token

        # Mock PyJWKClient and signing key
        mock_jwk_client = MockPyJWKClient.return_value
        mock_signing_key = MagicMock()
        mock_signing_key.key = "mocked_key"
        mock_jwk_client.get_signing_key_from_jwt.return_value = mock_signing_key

        client = OAuth2Client(auth_request)
        return client


def test_decode_token_success(oauth2client):
    with patch("jwt.decode", return_value={"some": "payload"}) as mock_jwt_decode:
        payload = oauth2client.decode_token()
        mock_jwt_decode.assert_called_once_with(
            "test_access_token",
            "mocked_key",
            algorithms=["RS256"],
            audience="test_client_id",
        )
        assert payload == {"some": "payload"}


def test_decode_token_expired(oauth2client):
    with patch("jwt.decode", side_effect=ExpiredSignatureError):
        with pytest.raises(ExpiredSignatureError):
            oauth2client.decode_token()


def test_is_expired_false(oauth2client):
    with patch("jwt.decode", return_value={"some": "payload"}):
        assert not oauth2client.is_expired


def test_is_expired_true(oauth2client):
    with patch("jwt.decode", side_effect=ExpiredSignatureError):
        assert oauth2client.is_expired


def test_refresh_token_success(oauth2client):
    new_token = {"access_token": "new_access_token"}

    def mock_fetch_token(*args, **kwargs):  # noqa
        oauth2client.session.token = new_token
        return new_token

    with patch.object(
        oauth2client.session, "fetch_token", side_effect=mock_fetch_token
    ) as mock_fetch_token_method, patch.object(
        oauth2client, "_get_signing_key"
    ) as mock_get_signing_key:
        oauth2client.refresh_token()

        mock_fetch_token_method.assert_called_once_with(
            token_url=oauth2client.auth_request.token_url,
            client_id=oauth2client.auth_request.client_id,
            client_secret=oauth2client.auth_request.client_secret,
            scope=oauth2client.auth_request.scope,
            include_client_id=True,
            client_kwargs={"tsg_id": oauth2client.auth_request.tsg_id},
        )
        mock_get_signing_key.assert_called_once()
        assert oauth2client.session.token["access_token"] == "new_access_token"


def test_refresh_token_exception(oauth2client):
    with patch.object(
        oauth2client.session, "fetch_token", side_effect=Exception("Network Error")
    ):
        with pytest.raises(Exception) as exc_info:
            oauth2client.refresh_token()
        assert "Network Error" in str(exc_info.value)


def test_auth_request_model_with_scope():
    """Test AuthRequestModel when scope is explicitly provided"""
    auth_request = AuthRequestModel(
        client_id="test_client_id",
        client_secret="test_client_secret",
        tsg_id="test_tsg_id",
        scope="custom_scope",
    )
    assert auth_request.scope == "custom_scope"
    assert auth_request.tsg_id == "test_tsg_id"


def test_auth_request_model_scope_construction():
    """Test automatic scope construction when scope is not provided"""
    auth_request = AuthRequestModel(
        client_id="test_client_id",
        client_secret="test_client_secret",
        tsg_id="test_tsg_id",
    )
    assert auth_request.scope == "tsg_id:test_tsg_id"


def test_auth_request_model_missing_tsg_id():
    """Test that ValueError is raised when tsg_id is missing and scope is not provided"""
    with pytest.raises(ValueError) as exc_info:
        AuthRequestModel(
            client_id="test_client_id", client_secret="test_client_secret", tsg_id=None
        )
    assert "1 validation error for AuthRequestModel" in str(exc_info.value)
    assert "Value error, tsg_id is required to construct scope" in str(exc_info.value)


def test_auth_request_model_default_token_url():
    """Test that default token_url is set correctly"""
    auth_request = AuthRequestModel(
        client_id="test_client_id",
        client_secret="test_client_secret",
        tsg_id="test_tsg_id",
    )
    assert (
        auth_request.token_url
        == "https://auth.apps.paloaltonetworks.com/am/oauth2/access_token"
    )


def test_auth_request_model_custom_token_url():
    """Test that custom token_url overrides default"""
    custom_url = "https://custom.example.com/token"
    auth_request = AuthRequestModel(
        client_id="test_client_id",
        client_secret="test_client_secret",
        tsg_id="test_tsg_id",
        token_url=custom_url,
    )
    assert auth_request.token_url == custom_url
