# pan_scm_sdk/exceptions/__init__.py


class APIError(Exception):
    """Base class for API exceptions."""


class AuthenticationError(APIError):
    """Raised when authentication fails."""


class ValidationError(APIError):
    """Raised when data validation fails."""


class NotFoundError(APIError):
    """Raised when a requested resource is not found."""


class ConflictError(APIError):
    """Raised when there is a conflict in the request."""
