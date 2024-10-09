from pan_scm_sdk.auth.oauth2 import OAuth2Client
from pan_scm_sdk.models.auth import AuthRequest
from pan_scm_sdk.utils.logging import setup_logger
from pan_scm_sdk.exceptions import APIError

logger = setup_logger(__name__)

class APIClient:
    def __init__(self, auth_request: AuthRequest, api_base_url: str):
        self.api_base_url = api_base_url
        self.oauth_client = OAuth2Client(auth_request)
        self.session = self.oauth_client.session
        self.scope = f"tsg_id:{auth_request.tsg_id}"

    def request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.api_base_url}{endpoint}"
        logger.debug(f"Making {method} request to {url} with params {kwargs}")
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise APIError(f"API request failed: {str(e)}") from e

    def get(self, endpoint: str, **kwargs):
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request('POST', endpoint, **kwargs)

    # Implement other methods as needed
