# scm/client.py
from typing import Optional, Dict, Any

import requests

from scm.auth import OAuth2Client
from scm.models.auth import AuthRequestModel
from scm.utils.logging import setup_logger
from scm.exceptions import (
    APIError,
    ObjectAlreadyExistsError,
    ValidationError,
    BadRequestError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    MethodNotAllowedError,
    ConflictError,
    ReferenceNotZeroError,
    ServerError,
    VersionNotSupportedError,
    SessionTimeoutError,
)

logger = setup_logger(__name__)


class Scm:
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

        # Create the AuthRequestModel object
        try:
            auth_request = AuthRequestModel(
                client_id=client_id,
                client_secret=client_secret,
                tsg_id=tsg_id,
            )
        except ValueError as e:
            logger.error(f"Authentication initialization failed: {e}")
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
        logger.debug(f"Making {method} request to {url} with params {kwargs}")
        try:
            response = self.session.request(
                method,
                url,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            error_content = response.json() if response.content else {}
            logger.error(f"HTTP error occurred: {http_err} - {error_content}")
            exception = self._handle_api_error(
                response,
                error_content,
            )
            raise exception from http_err
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise APIError(f"API request failed: {str(e)}") from e

    @staticmethod
    def _handle_api_error(
        response,
        error_content,
    ):
        """
        Args:
            response: The HTTP response object returned from the API call.
            error_content: The parsed content of the error response from the API.

        Returns:
            An instance of an appropriate exception class based on the HTTP status code and error details provided in the response.
        """

        # extract status code from response
        status_code = response.status_code

        # extract error details
        error_details = error_content.get("_errors", [{}])[0]
        error_code = error_details.get("code", "")
        error_message = error_details.get("message", "An error occurred.")
        error_type = error_details.get("details", {}).get("errorType", "")
        request_id = error_content.get("_request_id")

        # Map HTTP status codes to exceptions
        # 400 Bad Request
        if status_code == 400:
            if error_type == "Object Already Exists":
                return ObjectAlreadyExistsError(
                    error_message,
                    error_code=error_code,
                    details=error_details,
                    request_id=request_id,
                )
            elif error_type == "Invalid Object":
                return ValidationError(
                    error_message,
                    error_code=error_code,
                    details=error_details,
                    request_id=request_id,
                )
            else:
                return BadRequestError(
                    error_message,
                    error_code=error_code,
                    details=error_details,
                    request_id=request_id,
                )

        # 401 Unauthorized
        elif status_code == 401:
            return AuthenticationError(
                error_message,
                error_code=error_code,
                details=error_details,
                request_id=request_id,
            )

        # 403 Forbidden
        elif status_code == 403:
            return AuthorizationError(
                error_message,
                error_code=error_code,
                details=error_details,
                request_id=request_id,
            )

        # 404 Not Found
        elif status_code == 404:
            return NotFoundError(
                error_message,
                error_code=error_code,
                details=error_details,
                request_id=request_id,
            )

        # 405 Method Not Allowed
        elif status_code == 405:
            return MethodNotAllowedError(
                error_message,
                error_code=error_code,
                details=error_details,
                request_id=request_id,
            )

        # 409 Conflict
        elif status_code == 409:
            if error_type == "Name Not Unique":
                return ConflictError(
                    error_message,
                    error_code=error_code,
                    details=error_details,
                    request_id=request_id,
                )
            elif error_type == "Reference Not Zero":
                return ReferenceNotZeroError(
                    error_message,
                    error_code=error_code,
                    details=error_details,
                    request_id=request_id,
                )
            else:
                return ConflictError(
                    error_message,
                    error_code=error_code,
                    details=error_details,
                    request_id=request_id,
                )

        # 500 Internal Server Error
        elif status_code == 500:
            return ServerError(
                error_message,
                error_code=error_code,
                details=error_details,
                request_id=request_id,
            )

        # 501 Not Implemented
        elif status_code == 501:
            return VersionNotSupportedError(
                error_message,
                error_code=error_code,
                details=error_details,
                request_id=request_id,
            )

        # 504 Gateway Timeout
        elif status_code == 504:
            return SessionTimeoutError(
                error_message,
                error_code=error_code,
                details=error_details,
                request_id=request_id,
            )
        else:
            return APIError(
                f"HTTP {status_code}: {error_message}",
                error_code=error_code,
                details=error_details,
                request_id=request_id,
            )

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
