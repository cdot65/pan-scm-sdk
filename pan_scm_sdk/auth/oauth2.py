from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from pan_scm_sdk.utils.logging import setup_logger
from pan_scm_sdk.models.auth import AuthRequest
import jwt
from jwt import PyJWKClient
from jwt.exceptions import ExpiredSignatureError

logger = setup_logger(__name__)

class OAuth2Client:
    def __init__(self, auth_request: AuthRequest):
        self.auth_request = auth_request
        self.session = self._create_session()
        self.signing_key = self._get_signing_key()
        self.scope = f"tsg_id:{auth_request.tsg_id}"

    def _create_session(self):
        client = BackendApplicationClient(client_id=self.auth_request.client_id)
        oauth = OAuth2Session(client=client, scope=self.auth_request.scope)
        logger.debug("Fetching token...")
        token = oauth.fetch_token(
            token_url=self.auth_request.token_url,
            client_id=self.auth_request.client_id,
            client_secret=self.auth_request.client_secret,
            include_client_id=True,
            client_kwargs={'tsg_id': self.auth_request.tsg_id}
        )
        logger.debug("Token fetched successfully.")
        return oauth

    def _get_signing_key(self):
        jwks_uri = "/".join(
            self.auth_request.token_url.split("/")[:-1]
        ) + "/connect/jwk_uri"
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
            include_client_id=True,
            client_kwargs={'tsg_id': self.auth_request.tsg_id}
        )
        logger.debug("Token refreshed successfully.")
        self.signing_key = self._get_signing_key()
