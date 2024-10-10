# scm/exceptions/__init__.py


class APIError(Exception):
    """Base class for API exceptions."""

    def __init__(self, message, error_code=None, details=None, request_id=None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details
        self.request_id = request_id


class AuthenticationError(APIError):
    """Raised when authentication fails."""


class AuthorizationError(APIError):
    """Raised when authorization fails (Forbidden access)."""


class BadRequestError(APIError):
    """Raised when the API request is invalid."""


class NotFoundError(APIError):
    """Raised when a requested resource is not found."""


class ConflictError(APIError):
    """Raised when there is a conflict in the request."""


class ServerError(APIError):
    """Raised when the server encounters an error."""


class ValidationError(APIError):
    """Raised when data validation fails."""


class ObjectAlreadyExistsError(ConflictError):
    """Raised when the object being created already exists."""


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


class ReferenceNotZeroError(ConflictError):
    """Raised when attempting to delete an object that is still referenced."""


class SessionExpiredError(AuthenticationError):
    """Raised when the session has expired."""
