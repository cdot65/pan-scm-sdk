# SCM Client

The `Scm` class provides methods to interact with the Palo Alto Networks Strata Cloud Manager API.

---

## Importing the Scm Class

<div class="termy">

```python
from scm.client import Scm
```

</div>

## Class: Scm

Manages authentication and API requests.

### Attributes

- `api_base_url` (str): Base URL for the API.
- `oauth_client` (OAuth2Client): OAuth2 client for authentication.
- `session` (requests.Session): HTTP session for requests.
- `logger` (Logger): Logger instance for SDK logging.

### Methods

- `__init__(client_id: str, client_secret: str, tsg_id: str, api_base_url: str, log_level: str = "ERROR")`: Initializes
  the client.
- `request(method: str, endpoint: str, **kwargs)`: Makes an HTTP request.
- `get(endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs)`: Makes a GET request.
- `post(endpoint: str, **kwargs)`: Makes a POST request.
- `put(endpoint: str, **kwargs)`: Makes a PUT request.
- `delete(endpoint: str, **kwargs)`: Makes a DELETE request.

## Exceptions

The SDK uses a hierarchical exception system for handling various API errors:

### Authentication Errors (HTTP 401)

- `AuthenticationError`: Base class for authentication failures
- `NotAuthenticatedError`: When not authenticated
- `InvalidCredentialError`: When credentials are invalid
- `KeyExpiredError`: When the API key has expired
- `PasswordChangeRequiredError`: When password change is required

### Authorization Errors (HTTP 403)

- `AuthorizationError`: Base class for authorization failures
- `UnauthorizedError`: When access is unauthorized

### Bad Request Errors (HTTP 400)

- `BadRequestError`: Base class for invalid requests
- `InputFormatMismatchError`: When request format is invalid
- `MissingQueryParameterError`: When required query parameter is missing
- `InvalidObjectError`: When provided object is invalid

### Not Found Errors (HTTP 404)

- `NotFoundError`: Base class for missing resources
- `ObjectNotPresentError`: When requested object doesn't exist

### Conflict Errors (HTTP 409)

- `ConflictError`: Base class for conflict errors
- `ObjectNotUniqueError`: When object uniqueness is violated
- `NameNotUniqueError`: When name is already in use

### Server Errors (HTTP 5xx)

- `ServerError`: Base class for server-side errors
- `APINotImplementedError`: When API endpoint is not implemented
- `GatewayTimeoutError`: When request times out

## Usage Example

<div class="termy">

```python
from scm.client import Scm
from scm.exceptions import AuthenticationError, NotFoundError

try:
    # Initialize with custom logging level
    api_client = Scm(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id",
        log_level="DEBUG"  # Set to DEBUG for detailed logging
    )

    # Import Address from SDK
    from scm.config.objects import Address

    addresses = Address(api_client)

    # List addresses with error handling
    try:
        result = addresses.list(folder='Prisma Access')
        print(f"Found {len(result)} addresses")

    except NotFoundError as e:
        print(f"Folder not found: {e}")
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")

except Exception as e:
    print(f"Failed to initialize client: {e}")
```

</div>

## Error Handling Example

Here's an example showing proper error handling with the SDK:

<div class="termy">

```python
from scm.client import Scm
from scm.exceptions import (
    AuthenticationError,
    NotFoundError,
    BadRequestError,
    ServerError
)


def handle_api_operation():
    try:
        client = Scm(
            client_id="your_client_id",
            client_secret="your_client_secret",
            tsg_id="your_tsg_id",
            log_level="INFO"
        )

        # Attempt API operation
        result = client.get("/v1/objects/addresses")
        return result

    except AuthenticationError as e:
        print(f"Authentication failed: {e.message}")
        print(f"Error code: {e.error_code}")
        print(f"HTTP status: {e.http_status_code}")

    except NotFoundError as e:
        print(f"Resource not found: {e.message}")

    except BadRequestError as e:
        print(f"Invalid request: {e.message}")
        print(f"Details: {e.details}")

    except ServerError as e:
        print(f"Server error occurred: {e.message}")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
```

</div>
