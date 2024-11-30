# scm/auth.py

# Standard libraries
import time
from typing import Optional

# External libraries
import jwt
from jwt import PyJWKClient
from jwt.exceptions import ExpiredSignatureError, DecodeError, PyJWKClientError
from oauthlib.oauth2 import BackendApplicationClient
from requests import Response, Session
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, Timeout, RequestException
from requests_oauthlib import OAuth2Session
from urllib3 import Retry

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
        signing_key (Optional[PyJWK]): The key used for verifying the JWT token.
    """

    MAX_RETRIES = 3
    RETRY_BACKOFF = 0.3
    TOKEN_EXPIRY_BUFFER = 300  # 5 minutes buffer before token expiry

    def __init__(
        self,
        auth_request: AuthRequestModel,
    ):
        self.auth_request = auth_request
        self.session = self._create_session()
        self.signing_key = None

        # Only fetch signing key if we have a valid token
        if self.session.token:
            self.signing_key = self._get_signing_key()

    def _setup_retry_strategy(self) -> Retry:
        """Configure retry strategy for failed requests."""
        return Retry(
            total=self.MAX_RETRIES,
            backoff_factor=self.RETRY_BACKOFF,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"],  # Allow retries on POST for token refresh
        )

    def _create_session(self) -> OAuth2Session:
        """Create an OAuth2 session with retry logic."""
        client = BackendApplicationClient(client_id=self.auth_request.client_id)
        oauth = OAuth2Session(client=client)

        # Configure retry strategy
        retry_strategy = self._setup_retry_strategy()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        oauth.mount("http://", adapter)  # noqa
        oauth.mount("https://", adapter)

        logger.debug("Fetching initial token...")

        try:
            oauth.fetch_token(
                token_url=self.auth_request.token_url,
                client_id=self.auth_request.client_id,
                client_secret=self.auth_request.client_secret,
                scope=self.auth_request.scope,
                include_client_id=True,
                client_kwargs={"tsg_id": self.auth_request.tsg_id},
                timeout=30,  # Add explicit timeout
            )
            logger.debug("Token fetched successfully.")
            return oauth

        except (ConnectionError, Timeout) as e:
            logger.error(f"Network error during token fetch: {str(e)}")
            raise APIError(f"Network error during session creation: {str(e)}") from e
        except HTTPError as e:
            response: Optional[Response] = e.response
            if response is not None and response.content:
                ErrorHandler.raise_for_error(response.json(), response.status_code)
            # raise APIError(f"HTTP error during session creation: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during token fetch: {str(e)}")
            raise APIError(f"Failed to create session: {str(e)}") from e

    def _get_signing_key(self):
        """Retrieve the signing key for JWT verification."""
        if not self.session.token:
            raise APIError("Cannot retrieve signing key: No token available.")

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
            logger.error(f"Failed to retrieve signing key: {str(e)}")
            raise APIError(f"Failed to retrieve signing key: {str(e)}") from e

    @property
    def token_expires_soon(self) -> bool:
        """Check if the token will expire soon, accounting for buffer time."""
        if not self.session.token:
            return True
        return (
            time.time()
            >= self.session.token.get("expires_at", 0) - self.TOKEN_EXPIRY_BUFFER
        )

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        try:
            if not self.session.token:
                return True
            jwt.decode(
                self.session.token["access_token"],
                self.signing_key.key if self.signing_key else None,
                algorithms=["RS256"],
                audience=self.auth_request.client_id,
            )
            return False
        except ExpiredSignatureError:
            return True
        except Exception as e:
            logger.error(f"Error checking token expiration: {str(e)}")
            raise APIError(f"Failed to decode token: {str(e)}") from e

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

    def refresh_token(self) -> None:
        """Refresh the OAuth2 access token with improved error handling and retry logic."""
        logger.debug("Refreshing token...")

        # Create a new session for the refresh request to avoid any stale state
        temp_session = Session()
        retry_strategy = self._setup_retry_strategy()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        temp_session.mount("http://", adapter)  # noqa
        temp_session.mount("https://", adapter)

        try:
            new_token = self.session.fetch_token(
                token_url=self.auth_request.token_url,
                client_id=self.auth_request.client_id,
                client_secret=self.auth_request.client_secret,
                scope=self.auth_request.scope,
                include_client_id=True,
                client_kwargs={"tsg_id": self.auth_request.tsg_id},
                timeout=30,  # Add explicit timeout
                verify=True,  # Ensure SSL verification
            )

            # Update session token
            self.session.token = new_token
            # Refresh signing key after token refresh
            self.signing_key = self._get_signing_key()

            logger.debug("Token refreshed successfully.")

        except (ConnectionError, Timeout) as e:
            logger.error(f"Network error during token refresh: {str(e)}")
            raise APIError(f"Network error during token refresh: {str(e)}") from e
        except HTTPError as e:
            response = e.response
            if response is not None and response.content:
                error_content = response.json()
                ErrorHandler.raise_for_error(error_content, response.status_code)
            else:
                raise APIError(
                    f"HTTP error occurred while refreshing token: {str(e)}"
                ) from e
        except RequestException as e:
            logger.error(f"Request error during token refresh: {str(e)}")
            raise APIError(f"Request failed during token refresh: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {str(e)}")
            raise APIError(f"Failed to refresh token: {str(e)}") from e
        finally:
            temp_session.close()
