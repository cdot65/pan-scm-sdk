# scm/auth.py

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from scm.utils.logging import setup_logger
from scm.models.auth import AuthRequestModel
import jwt
from jwt import PyJWKClient
from jwt.exceptions import ExpiredSignatureError

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

    Error:
        ExpiredSignatureError: Raised when the token has expired.

    Return:
        payload (dict): Decoded JWT token payload when using decode_token method.
    """

    def __init__(self, auth_request: AuthRequestModel):
        self.auth_request = auth_request
        self.session = self._create_session()
        self.signing_key = self._get_signing_key()

    def _create_session(self):
        client = BackendApplicationClient(client_id=self.auth_request.client_id)
        oauth = OAuth2Session(client=client)
        logger.debug("Fetching token...")

        token = oauth.fetch_token(
            token_url=self.auth_request.token_url,
            client_id=self.auth_request.client_id,
            client_secret=self.auth_request.client_secret,
            scope=self.auth_request.scope,
            include_client_id=True,
            client_kwargs={"tsg_id": self.auth_request.tsg_id},
        )
        logger.debug(f"Token fetched successfully. {token}")
        return oauth

    def _get_signing_key(self):
        jwks_uri = (
            "/".join(self.auth_request.token_url.split("/")[:-1]) + "/connect/jwk_uri"
        )
        jwks_client = PyJWKClient(jwks_uri)
        signing_key = jwks_client.get_signing_key_from_jwt(
            self.session.token["access_token"]
        )
        return signing_key

    def decode_token(self):
        try:
            payload = jwt.decode(
                self.session.token["access_token"],
                self.signing_key.key,
                algorithms=["RS256"],
                audience=self.auth_request.client_id,
            )
            return payload
        except ExpiredSignatureError:
            logger.error("Token has expired.")
            raise

    @property
    def is_expired(self):
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

    def refresh_token(self):
        logger.debug("Refreshing token...")
        token = self.session.fetch_token(
            token_url=self.auth_request.token_url,
            client_id=self.auth_request.client_id,
            client_secret=self.auth_request.client_secret,
            scope=self.auth_request.scope,
            include_client_id=True,
            client_kwargs={"tsg_id": self.auth_request.tsg_id},
        )
        logger.debug(f"Token refreshed successfully. {token}")
        self.signing_key = self._get_signing_key()
