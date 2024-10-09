class APIError(Exception):
    """Base class for API exceptions."""

class AuthenticationError(APIError):
    """Raised when authentication fails."""

class ValidationError(APIError):
    """Raised when data validation fails."""
