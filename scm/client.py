# scm/client.py

# Standard library imports
import logging
import sys
from typing import Optional, Dict, Any

# External libraries
from requests.exceptions import HTTPError

# Local SDK imports
from scm.auth import OAuth2Client
from scm.exceptions import (
    APIError,
    ErrorHandler,
)
from scm.models.auth import AuthRequestModel


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
        log_level: str = "ERROR",
    ):
        self.api_base_url = api_base_url

        # Map string log level to numeric level
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {log_level}")

        # Configure the 'scm' logger
        self.logger = logging.getLogger("scm")
        self.logger.setLevel(numeric_level)

        # Add a handler if the logger doesn't have one
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(numeric_level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Create the AuthRequestModel object
        try:
            auth_request = AuthRequestModel(
                client_id=client_id,
                client_secret=client_secret,
                tsg_id=tsg_id,
            )
        except ValueError as e:
            # Let exception propagate
            raise APIError(f"Authentication initialization failed: {e}") from e

        self.logger.debug(f"Auth request: {auth_request.model_dump()}")
        self.oauth_client = OAuth2Client(auth_request)
        self.session = self.oauth_client.session
        self.logger.debug(f"Session created: {self.session.headers}")

    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ):
        """
        Handles the API request and returns the response JSON or None if no content is present.

        Args:
            method: HTTP method to be used for the request (e.g., 'GET', 'POST').
            endpoint: The API endpoint to which the request is made.
            **kwargs: Additional arguments to be passed to the request (e.g., headers, params, data).
        """
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

        except HTTPError as e:
            # Handle HTTP errors
            response = e.response
            if response is not None and response.content:
                error_content = response.json()
                ErrorHandler.raise_for_error(
                    error_content,
                    response.status_code,
                )
            else:
                raise APIError(f"HTTP error occurred: {e}") from e

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Sends a GET request to the SCM API.
        """
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request(
            "GET",
            endpoint,
            params=params,
            **kwargs,
        )

    def post(
        self,
        endpoint: str,
        **kwargs,
    ):
        """
        Sends a POST request to the SCM API.
        """
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request(
            "POST",
            endpoint,
            **kwargs,
        )

    def put(
        self,
        endpoint: str,
        **kwargs,
    ):
        """
        Sends a PUT request to the SCM API.
        """
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request(
            "PUT",
            endpoint,
            **kwargs,
        )

    def delete(
        self,
        endpoint: str,
        **kwargs,
    ):
        """
        Sends a DELETE request to the SCM API.
        """
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request(
            "DELETE",
            endpoint,
            **kwargs,
        )
