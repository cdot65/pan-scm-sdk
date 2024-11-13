# scm/client.py
from typing import Optional, Dict, Any
import logging
import requests

from scm.auth import OAuth2Client
from scm.models.auth import AuthRequestModel
from scm.utils.logging import setup_logger
from scm.exceptions import (
    APIError,
    ErrorHandler,
)


class Scm:
    """
    A client for interacting with the Palo Alto Networks Strata Cloud Manager API.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tsg_id: str,
        api_base_url: str = "https://api.strata.paloaltonetworks.com",
        log_level: int = logging.ERROR,
    ):
        self.api_base_url = api_base_url

        # Set up logger with user-specified log level
        self.logger = setup_logger(__name__, log_level=log_level)

        # Create the AuthRequestModel object
        try:
            auth_request = AuthRequestModel(
                client_id=client_id,
                client_secret=client_secret,
                tsg_id=tsg_id,
            )
        except ValueError as e:
            self.logger.error(f"Authentication initialization failed: {e}")
            raise APIError(f"Authentication initialization failed: {e}")

        self.oauth_client = OAuth2Client(auth_request)
        self.session = self.oauth_client.session

    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ):
        url = f"{self.api_base_url}{endpoint}"
        self.logger.debug(f"Making {method} request to {url} with params {kwargs}")
        try:
            response = self.session.request(
                method,
                url,
                **kwargs,
            )
            response.raise_for_status()
            if response.content and response.content.strip():
                return response.json()
            else:
                return None  # Return None or an empty dict
        except requests.exceptions.HTTPError as http_err:
            http_status_code = response.status_code
            error_content = response.json() if response.content else {}
            self.logger.error(f"HTTP error occurred: {http_err} - {error_content}")
            ErrorHandler.raise_for_error(
                error_content,
                http_status_code,
            )
        except Exception as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise APIError(f"API request failed: {str(e)}") from e

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs):
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request("GET", endpoint, params=params, **kwargs)

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
