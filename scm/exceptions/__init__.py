# scm/exceptions/__init__.py

from dataclasses import dataclass
from typing import Optional, Dict, Any, Type, Union, List


@dataclass
class ErrorResponse:
    """Represents a standardized API error response."""

    code: str
    message: str
    details: Optional[Union[Dict[str, Any], List[Any]]] = None

    @classmethod
    def from_response(cls, response_data: Dict[str, Any]) -> "ErrorResponse":
        if "_errors" not in response_data or not response_data["_errors"]:
            raise ValueError("Invalid error response format")

        error = response_data["_errors"][0]
        return cls(
            code=error.get("code", ""),
            message=error.get("message", ""),
            details=error.get("details"),
        )


class APIError(Exception):
    """Base class for all API exceptions."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        http_status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.http_status_code = http_status_code
        self.details = details

    def __str__(self):
        parts = []
        # if self.message:
        #     parts.append(f"{self.message}")
        if self.details:
            parts.append(f"{self.details}")
        if self.http_status_code is not None:
            parts.append(f"HTTP error: {self.http_status_code}")
        if self.error_code:
            parts.append(f"API error: {self.error_code}")
        return " - ".join(parts)


# Base classes for HTTP status codes
class ClientError(APIError):
    """Base class for 4xx client errors."""


class ServerError(APIError):
    """Base class for 5xx server errors."""


# Authentication Errors (HTTP 401)
class AuthenticationError(ClientError):
    """Raised when authentication fails (HTTP 401 Unauthorized)."""


class NotAuthenticatedError(AuthenticationError):
    """Raised when not authenticated (E016: Not Authenticated)."""


class InvalidCredentialError(AuthenticationError):
    """Raised when credentials are invalid (E016: Invalid Credential)."""


class KeyTooLongError(AuthenticationError):
    """Raised when the key is too long (E016: Key Too Long)."""


class KeyExpiredError(AuthenticationError):
    """Raised when the key has expired (E016: Key Expired)."""


class PasswordChangeRequiredError(AuthenticationError):
    """Raised when a password change is required (E016: The password needs to be changed)."""


# Access Errors (HTTP 403)
class AuthorizationError(ClientError):
    """Raised when authorization fails (HTTP 403 Forbidden)."""


class UnauthorizedError(AuthorizationError):
    """Raised when unauthorized access is attempted (E007: Unauthorized)."""


# Bad Request Errors (HTTP 400)
class BadRequestError(ClientError):
    """Raised for bad requests (HTTP 400 Bad Request)."""


class InputFormatMismatchError(BadRequestError):
    """Raised when input format mismatches (E003: Input Format Mismatch)."""


class OutputFormatMismatchError(BadRequestError):
    """Raised when output format mismatches (E003: Output Format Mismatch)."""


class MissingQueryParameterError(BadRequestError):
    """Raised when a query parameter is missing (E003: Missing Query Parameter)."""


class InvalidQueryParameterError(BadRequestError):
    """Raised when a query parameter is invalid (E003: Invalid Query Parameter)."""


class MissingBodyError(BadRequestError):
    """Raised when the request body is missing (E003: Missing Body)."""


class InvalidObjectError(BadRequestError):
    """Raised when an invalid object is provided (E003: Invalid Object)."""


class InvalidCommandError(BadRequestError):
    """Raised when an invalid command is issued (E003: Invalid Command)."""


class MalformedCommandError(BadRequestError):
    """Raised when a command is malformed (E003: Malformed Command)."""


class BadXPathError(BadRequestError):
    """Raised when an invalid XPath is used (E013: Bad XPath)."""


# Not Found Errors (HTTP 404)
class NotFoundError(ClientError):
    """Raised when a resource is not found (HTTP 404 Not Found)."""


class ObjectNotPresentError(NotFoundError):
    """Raised when the object is not present (E005: Object Not Present)."""


# Conflict Errors (HTTP 409)
class ConflictError(ClientError):
    """Raised when there is a conflict (HTTP 409 Conflict)."""


class ObjectNotUniqueError(ConflictError):
    """Raised when the object is not unique (E016: Object Not Unique)."""


class NameNotUniqueError(ConflictError):
    """Raised when the name is not unique (E006: Name Not Unique)."""


class ReferenceNotZeroError(ConflictError):
    """Raised when the reference count is not zero (E009: Reference Not Zero)."""


# Method Not Allowed (HTTP 405)
class MethodNotAllowedError(ClientError):
    """Raised when the method is not allowed (HTTP 405 Method Not Allowed)."""


class ActionNotSupportedError(MethodNotAllowedError):
    """Raised when the action is not supported (E012: Action Not Supported)."""


# Not Implemented (HTTP 501)
class APINotImplementedError(ServerError):
    """Raised when a method is not implemented (HTTP 501 Not Implemented)."""


class VersionAPINotSupportedError(APINotImplementedError):
    """Raised when the API version is not supported (E012: Version Not Supported)."""


class MethodAPINotSupportedError(APINotImplementedError):
    """Raised when the method is not supported (E012: Method Not Supported)."""


# Gateway Timeout (HTTP 504)
class GatewayTimeoutError(ServerError):
    """Raised when a gateway timeout occurs (HTTP 504 Gateway Timeout)."""


class SessionTimeoutError(GatewayTimeoutError):
    """Raised when the session times out (Code '4': Session Timeout)."""


class ErrorHandler:
    """Handles mapping of API error responses to appropriate exceptions."""

    # Map HTTP status codes to base exception classes
    ERROR_STATUS_CODE_MAP: Dict[int, Type[APIError]] = {
        400: BadRequestError,
        401: AuthenticationError,
        403: AuthorizationError,
        404: NotFoundError,
        405: MethodNotAllowedError,
        409: ConflictError,
        500: ServerError,
        501: APINotImplementedError,
        504: GatewayTimeoutError,
    }

    # Map error codes to specific exception classes
    ERROR_CODE_MAP: Dict[str, Union[Type[APIError], Dict[str, Type[APIError]]]] = {
        "API_I00013": {
            "object not present": ObjectNotPresentError,
            "operation impossible": ObjectNotPresentError,
            "object already exists": NameNotUniqueError,
            "object_already_exists": NameNotUniqueError,
            "non_zero_refs": ReferenceNotZeroError,
            "reference not zero": ReferenceNotZeroError,
            "malformed command": MalformedCommandError,
        },
        "API_I00035": InvalidObjectError,
        "E003": {
            "Input Format Mismatch": InputFormatMismatchError,
            "Output Format Mismatch": OutputFormatMismatchError,
            "Missing Query Parameter": MissingQueryParameterError,
            "Invalid Query Parameter": InvalidQueryParameterError,
            "Missing Body": MissingBodyError,
            "Invalid Object": InvalidObjectError,
            "Invalid Command": InvalidCommandError,
            "Malformed Command": MalformedCommandError,
        },
        "E005": ObjectNotPresentError,
        "E006": NameNotUniqueError,
        "E007": UnauthorizedError,
        "E009": ReferenceNotZeroError,
        "E012": {
            "Version Not Supported": VersionAPINotSupportedError,
            "Method Not Supported": MethodAPINotSupportedError,
            "Action Not Supported": ActionNotSupportedError,
        },
        "E013": BadXPathError,
        "E016": {
            "Not Authenticated": NotAuthenticatedError,
            "Invalid Credential": InvalidCredentialError,
            "Key Too Long": KeyTooLongError,
            "Key Expired": KeyExpiredError,
            "The password needs to be changed.": PasswordChangeRequiredError,
            "Object Not Unique": ObjectNotUniqueError,
        },
        "4": SessionTimeoutError,
    }

    @classmethod
    def raise_for_error(
        cls,
        response_data: Dict[str, Any],
        http_status_code: int,
    ) -> None:

        # Perform the mapping of the error response from the provided response data
        error_response = ErrorResponse.from_response(response_data)

        # Get base exception class from HTTP status code
        exception_cls = cls.ERROR_STATUS_CODE_MAP.get(http_status_code, APIError)

        # Refine exception class based on error code and message
        error_code = error_response.code
        message = error_response.message
        error_details = error_response.details
        error_type = None

        # Extract errorType from error_details
        if isinstance(error_details, dict):
            error_type = error_details.get("errorType")

            # If errorType is not found, check inside the 'errors' list
            if not error_type and "errors" in error_details:
                errors_list = error_details["errors"]
                if isinstance(errors_list, list) and len(errors_list) > 0:
                    error_type = errors_list[0].get("type")

        # Now, attempt to match the error_type
        if error_code in cls.ERROR_CODE_MAP:
            code_mapping = cls.ERROR_CODE_MAP[error_code]

            # if code_mapping is of type dictionary
            if isinstance(code_mapping, dict):

                # Try to match errorType (case-insensitive)
                if error_type:
                    error_type_lower = error_type.lower()
                    code_mapping_lower = {k.lower(): v for k, v in code_mapping.items()}

                    # First, try to match errorType
                    if error_type_lower in code_mapping_lower:
                        exception_cls = code_mapping_lower[error_type_lower]

                    # Then, try to match message
                    elif message in code_mapping:
                        exception_cls = code_mapping[message]

                    # Default to base exception
                    else:
                        exception_cls = exception_cls

                # Default to base exception
                else:
                    exception_cls = exception_cls

            # if code_mapping is not of type dictionary, set exception_cls to code_mapping
            else:
                exception_cls = code_mapping

        raise exception_cls(
            message=message,
            error_code=error_code,
            http_status_code=http_status_code,
            details=error_details,
        )
