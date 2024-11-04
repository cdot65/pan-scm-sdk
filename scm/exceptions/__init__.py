# scm/exceptions/__init__.py

from typing import Dict, Any, Optional, Type, List, Union
from dataclasses import dataclass


@dataclass
class ReferenceDetail:
    """Represents details about an object reference."""

    type: str
    message: str
    params: List[str]
    extra: List[str]


@dataclass
class ErrorResponse:
    """Represents a standardized API error response."""

    code: str
    message: str
    details: Optional[Union[Dict[str, Any], List[str]]] = None
    request_id: Optional[str] = None

    @classmethod
    def from_response(cls, response_data: Dict[str, Any]) -> "ErrorResponse":
        if "_errors" not in response_data or not response_data["_errors"]:
            raise ValueError("Invalid error response format")

        error = response_data["_errors"][0]
        return cls(
            code=error.get("code", ""),
            message=error.get("message", ""),
            details=error.get("details", {}),
            request_id=response_data.get("_request_id"),
        )


class APIError(Exception):
    """Base class for API exceptions."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        references: Optional[List[str]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.request_id = request_id
        self.references = references or []

    @classmethod
    def from_error_response(cls, error_response: ErrorResponse) -> "APIError":
        """Creates an APIError instance from an ErrorResponse."""
        return cls(
            message=error_response.message,
            error_code=error_response.code,
            details=error_response.details,
            request_id=error_response.request_id,
        )


class AuthenticationError(APIError):
    """Raised when authentication fails."""


class AuthorizationError(APIError):
    """Raised when authorization fails (Forbidden access)."""


class BadRequestError(APIError):
    """Raised when the API request is invalid."""


class NotFoundError(APIError):
    """Raised when a requested resource is not found."""


class ObjectNotPresentError(NotFoundError):
    """Raised when a specific object is not found."""


class FolderNotFoundError(NotFoundError):
    """Raised when a specified folder does not exist."""


class ConflictError(APIError):
    """Raised when there is a conflict in the request."""


class ServerError(APIError):
    """Raised when the server encounters an error."""


class ValidationError(APIError):
    """Raised when data validation fails."""


class EmptyFieldError(ValidationError):
    """Raised when a required field is empty."""


class MalformedRequestError(APIError):
    """Raised when the request is malformed."""


class ObjectAlreadyExistsError(APIError):
    """Raised when attempting to create an object that already exists."""


class SessionTimeoutError(APIError):
    """Raised when the session has timed out."""


class MethodNotAllowedError(APIError):
    """Raised when the HTTP method is not allowed."""


class InvalidCommandError(BadRequestError):
    """Raised when an invalid command is sent to the API."""


class InvalidParameterError(BadRequestError):
    """Raised when a query parameter is invalid."""


class MissingParameterError(BadRequestError):
    """Raised when a required parameter is missing."""


class InputFormatError(BadRequestError):
    """Raised when the input format is incorrect."""


class OutputFormatError(BadRequestError):
    """Raised when the output format is incorrect."""


class VersionNotSupportedError(APIError):
    """Raised when the API version is not supported."""


class ActionNotSupportedError(MethodNotAllowedError):
    """Raised when the requested action is not supported."""


class ReferenceNotZeroError(APIError):
    """
    Raised when attempting to delete an object that is still being referenced by other objects.

    Attributes:
        references (List[str]): List of references to the object preventing deletion
        reference_paths (List[str]): Full paths to the referring objects
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        references: Optional[List[str]] = None,
        reference_paths: Optional[List[str]] = None,
    ):
        super().__init__(message, error_code, details, request_id, references)
        self.reference_paths = reference_paths or []

        # Format a more detailed error message
        ref_details = "\n".join([f"- {path}" for path in (self.reference_paths or [])])
        self.detailed_message = (
            f"{message}\n"
            f"This object cannot be deleted because it is referenced by:\n{ref_details}"
        )

    def __str__(self):
        return self.detailed_message


class SessionExpiredError(AuthenticationError):
    """Raised when the session has expired."""


class ErrorHandler:
    """Handles mapping of API error responses to appropriate exceptions."""

    # Map API error codes to exception classes
    ERROR_CODE_MAP: Dict[str, Type[APIError]] = {
        "API_I00013": NotFoundError,  # Generic not found error - will be refined by error type
        "API_I00035": ValidationError,  # Invalid request payload - will be refined by details
    }

    # Map error types from details to exception classes
    ERROR_TYPE_MAP: Dict[str, Type[APIError]] = {
        "Object Not Present": ObjectNotPresentError,
        "Operation Impossible": FolderNotFoundError,
        "Object Already Exists": ObjectAlreadyExistsError,
        "Malformed Command": MalformedRequestError,
    }

    @classmethod
    def raise_for_error(cls, response_data: Dict[str, Any]) -> None:
        """
        Raises the appropriate exception based on the API error response.

        Args:
            response_data: The error response from the API

        Raises:
            APIError: An appropriate subclass of APIError based on the error response
        """
        try:
            error_response = ErrorResponse.from_response(response_data)
        except ValueError:
            raise APIError("Invalid error response format")

        # Handle validation errors with empty fields
        if error_response.code == "API_I00013":
            if isinstance(error_response.details, dict):
                error_type = error_response.details.get("errorType")

                if error_type == "Reference Not Zero":
                    # Extract reference details
                    errors = error_response.details.get("errors", [])
                    references = []
                    reference_paths = []

                    for error in errors:
                        if isinstance(error, dict):
                            if "params" in error:
                                references.extend(error["params"])
                            if "extra" in error:
                                reference_paths.extend(error["extra"])

                    # Get the reference paths from the message if available
                    if "message" in error_response.details and isinstance(
                        error_response.details["message"], list
                    ):
                        reference_paths.extend(error_response.details["message"])

                    raise ReferenceNotZeroError(
                        message="Cannot delete object due to existing references",
                        error_code=error_response.code,
                        details=error_response.details,
                        request_id=response_data.get("_request_id"),
                        references=references,
                        reference_paths=reference_paths,
                    )

        # Get base exception class from error code
        exception_cls = cls.ERROR_CODE_MAP.get(error_response.code)

        # Refine exception class based on error type if available
        if isinstance(error_response.details, dict):
            error_type = error_response.details.get("errorType")
            if error_type and error_type in cls.ERROR_TYPE_MAP:
                exception_cls = cls.ERROR_TYPE_MAP[error_type]

        # Fall back to generic APIError if no specific match
        if not exception_cls:
            exception_cls = APIError

        # Include the detailed message if available
        if (
            isinstance(error_response.details, dict)
            and "message" in error_response.details
        ):
            message = error_response.details["message"]
        else:
            message = error_response.message

        raise exception_cls(
            message=message,
            error_code=error_response.code,
            details=error_response.details,
            request_id=error_response.request_id,
        )
