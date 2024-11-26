# scm/auth.py
from typing import Optional

# External libraries
import jwt
from jwt import PyJWKClient
from jwt.exceptions import ExpiredSignatureError, DecodeError, PyJWKClientError
from oauthlib.oauth2 import BackendApplicationClient
from requests import Response
from requests.exceptions import HTTPError
from requests_oauthlib import OAuth2Session

# Local SDK imports
from scm.exceptions import APIError, ErrorHandler
from scm.models.auth import AuthRequestModel
from scm.utils.logging import setup_logger

logger = setup_logger(__name__)


class OAuth2Client:
    """
    A client for OAuth2 authentication with Palo Alto Networks' Strata Cloud Manager.

    This class handles OAuth2 token acquisition, validation, and refresh for authenticating
    with Palo Alto Networks' services. It supports token decoding and expiration checking.

    Attributes:
        auth_request (AuthRequestModel): An object containing authentication parameters.
        session (OAuth2Session): The authenticated OAuth2 session.
        signing_key (PyJWK): The key used for verifying the JWT token.
    """

    def __init__(
        self,
        auth_request: AuthRequestModel,
    ):
        self.auth_request = auth_request
        self.session = self._create_session()
        self.signing_key = self._get_signing_key()

    def _create_session(self):
        """Create an OAuth2 session."""
        client = BackendApplicationClient(client_id=self.auth_request.client_id)
        oauth = OAuth2Session(client=client)
        logger.debug("Fetching token...")

        try:
            oauth.fetch_token(
                token_url=self.auth_request.token_url,
                client_id=self.auth_request.client_id,
                client_secret=self.auth_request.client_secret,
                scope=self.auth_request.scope,
                include_client_id=True,
                client_kwargs={"tsg_id": self.auth_request.tsg_id},
            )
            logger.debug("Token fetched successfully.")
            return oauth

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:
                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
        except Exception as e:
            # Let other exceptions propagate
            raise APIError(f"Failed to create session: {e}") from e

    def _get_signing_key(self):
        """Retrieve the signing key for JWT verification."""
        try:
            jwks_uri = (
                "/".join(self.auth_request.token_url.split("/")[:-1])
                + "/connect/jwk_uri"
            )
            jwks_client = PyJWKClient(jwks_uri)
            signing_key = jwks_client.get_signing_key_from_jwt(
                self.session.token["access_token"]
            )
            return signing_key
        except (PyJWKClientError, DecodeError) as e:
            raise APIError(f"Failed to retrieve signing key: {e}") from e

    def decode_token(self):
        """Decode the access token to retrieve payload."""
        try:
            payload = jwt.decode(
                self.session.token["access_token"],
                self.signing_key.key,
                algorithms=["RS256"],
                audience=self.auth_request.client_id,
            )
            return payload
        except ExpiredSignatureError:
            # Let the exception propagate without logging
            raise
        except Exception as e:
            raise APIError(f"Failed to decode token: {e}") from e

    @property
    def is_expired(self):
        """Check if the token has expired."""
        try:
            jwt.decode(
                self.session.token["access_token"],
                self.signing_key.key,
                algorithms=["RS256"],
                audience=self.auth_request.client_id,
            )
            return False
        except ExpiredSignatureError:
            return True
        except Exception as e:
            raise APIError(f"Failed to decode token: {e}") from e

    def refresh_token(self):
        """Refresh the OAuth2 access token."""
        logger.debug("Refreshing token...")
        try:
            self.session.fetch_token(
                token_url=self.auth_request.token_url,
                client_id=self.auth_request.client_id,
                client_secret=self.auth_request.client_secret,
                scope=self.auth_request.scope,
                include_client_id=True,
                client_kwargs={"tsg_id": self.auth_request.tsg_id},
            )
            logger.debug("Token refreshed successfully.")
            self.signing_key = self._get_signing_key()
        except HTTPError as e:
            response = e.response
            if response is not None and response.content:
                error_content = response.json()
                ErrorHandler.raise_for_error(error_content, response.status_code)
            else:
                raise APIError(
                    f"HTTP error occurred while refreshing token: {e}"
                ) from e
        except Exception as e:
            raise APIError(f"Failed to refresh token: {e}") from e
