# Exceptions Module

## Overview

The exceptions module provides a comprehensive error handling system for the SCM (Strata Cloud Manager) API. It includes
a standardized error response format and a hierarchy of exception classes that map to different types of API errors. The
module helps in handling and raising appropriate exceptions based on HTTP status codes and API-specific error codes.

## Core Components

### ErrorResponse

A dataclass that represents a standardized API error response.

```python
@dataclass
class ErrorResponse:
    code: str
    message: str
    details: Optional[Union[Dict[str, Any], List[Any]]] = None
```

#### Attributes

- `code`: The error code returned by the API
- `message`: A human-readable error message
- `details`: Additional error details (optional)

#### Methods

- `from_response(response_data: Dict[str, Any]) -> ErrorResponse`: Creates an ErrorResponse instance from API response
  data

### Base Exception Classes

#### APIError

The base class for all API exceptions.

**Attributes:**

- `message`: Error message
- `error_code`: API-specific error code
- `http_status_code`: HTTP status code
- `details`: Additional error details

#### Main Exception Categories

- `ClientError`: Base class for 4xx client errors
- `ServerError`: Base class for 5xx server errors

## Exception Hierarchy

### Authentication Errors (HTTP 401)

All inherit from `AuthenticationError`:

- `NotAuthenticatedError`: Not authenticated (E016)
- `InvalidCredentialError`: Invalid credentials (E016)
- `KeyTooLongError`: Authentication key too long (E016)
- `KeyExpiredError`: Authentication key expired (E016)
- `PasswordChangeRequiredError`: Password change required (E016)

### Authorization Errors (HTTP 403)

All inherit from `AuthorizationError`:

- `UnauthorizedError`: Unauthorized access attempt (E007)

### Bad Request Errors (HTTP 400)

All inherit from `BadRequestError`:

- `InputFormatMismatchError`: Input format mismatch (E003)
- `OutputFormatMismatchError`: Output format mismatch (E003)
- `MissingQueryParameterError`: Missing query parameter (E003)
- `InvalidQueryParameterError`: Invalid query parameter (E003)
- `MissingBodyError`: Missing request body (E003)
- `InvalidObjectError`: Invalid object provided (E003)
- `InvalidCommandError`: Invalid command issued (E003)
- `MalformedCommandError`: Malformed command (E003)
- `BadXPathError`: Invalid XPath used (E013)

### Not Found Errors (HTTP 404)

All inherit from `NotFoundError`:

- `ObjectNotPresentError`: Object not found (E005)

### Conflict Errors (HTTP 409)

All inherit from `ConflictError`:

- `ObjectNotUniqueError`: Object not unique (E016)
- `NameNotUniqueError`: Name not unique (E006)
- `ReferenceNotZeroError`: Reference count not zero (E009)

### Method Not Allowed Errors (HTTP 405)

All inherit from `MethodNotAllowedError`:

- `ActionNotSupportedError`: Action not supported (E012)

### Not Implemented Errors (HTTP 501)

All inherit from `APINotImplementedError`:

- `VersionAPINotSupportedError`: API version not supported (E012)
- `MethodAPINotSupportedError`: Method not supported (E012)

### Gateway Timeout Errors (HTTP 504)

All inherit from `GatewayTimeoutError`:

- `SessionTimeoutError`: Session timeout (Code '4')

## Error Handler

The `ErrorHandler` class provides centralized error handling functionality for the API.

### Key Components

#### Status Code Mapping

Maps HTTP status codes to base exception classes:

```python
ERROR_STATUS_CODE_MAP = {
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
```

#### Error Code Mapping

Maps API error codes and messages to specific exception classes. Supports both direct mappings and nested mappings based
on error messages or types.

### Usage

The `raise_for_error` class method handles error response mapping:

```python
@classmethod
def raise_for_error(
        cls,
        response_data: Dict[str, Any],
        http_status_code: int,
) -> None:
```

This method:

1. Creates an ErrorResponse from the API response data
2. Determines the appropriate exception class based on:
    - HTTP status code
    - Error code
    - Error type
    - Error message
3. Raises the appropriate exception with all relevant details

## Example Usage

```python
try:
    # API call that results in an error
    response_data = {
        "_errors": [{
            "code": "E016",
            "message": "Invalid Credential",
            "details": {"errorType": "invalid_credential"}
        }]
    }
    ErrorHandler.raise_for_error(response_data, 401)
except InvalidCredentialError as e:
    print(f"Authentication failed: {e}")
except APIError as e:
    print(f"General API error: {e}")
```