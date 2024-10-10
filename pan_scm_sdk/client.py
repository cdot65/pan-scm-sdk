# pan_scm_sdk/client.py
import requests

from pan_scm_sdk.auth.oauth2 import OAuth2Client
from pan_scm_sdk.models.auth import AuthRequest
from pan_scm_sdk.utils.logging import setup_logger
from pan_scm_sdk.exceptions import APIError

logger = setup_logger(__name__)


class APIClient:
    """
    A client for interacting with the Palo Alto Networks Strata Cloud Manager API.

    This class provides methods for authenticating and making HTTP requests to the Strata API,
    including GET, POST, PUT, and DELETE operations. It handles token refresh automatically.

    Attributes:
        api_base_url (str): The base URL for the Strata API.
        oauth_client (OAuth2Client): An instance of the OAuth2Client for authentication.
        session (requests.Session): A session object for making HTTP requests.

    Error:
        APIError: Raised when API initialization or requests fail.

    Return:
        dict: JSON response from the API for successful requests.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tsg_id: str,
        api_base_url: str = "https://api.strata.paloaltonetworks.com",
    ):
        self.api_base_url = api_base_url

        # Create the AuthRequest object
        try:
            auth_request = AuthRequest(
                client_id=client_id, client_secret=client_secret, tsg_id=tsg_id
            )
        except ValueError as e:
            logger.error(f"Authentication initialization failed: {e}")
            raise APIError(f"Authentication initialization failed: {e}")

        self.oauth_client = OAuth2Client(auth_request)
        self.session = self.oauth_client.session

    def request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.api_base_url}{endpoint}"
        logger.debug(f"Making {method} request to {url} with params {kwargs}")
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            error_content = response.json() if response.content else {}
            logger.error(f"HTTP error occurred: {http_err} - {error_content}")
            raise APIError(
                f"HTTP error occurred: {http_err} - {error_content}"
            ) from http_err
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise APIError(f"API request failed: {str(e)}") from e

    def get(self, endpoint: str, **kwargs):
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs):
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request("DELETE", endpoint, **kwargs)
