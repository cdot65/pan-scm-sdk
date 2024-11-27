# Client Module

## Overview

The SCM (Strata Cloud Manager) client module provides the primary interface for interacting with the Palo Alto Networks
Strata Cloud Manager API. It handles authentication, request management, and provides a clean interface for making API
calls with proper error handling.

## SCM Client

### Class Definition

<div class="termy">

<!-- termynal -->

```python
class Scm:
    def __init__(
            self,
            client_id: str,
            client_secret: str,
            tsg_id: str,
            api_base_url: str,
            log_level: str = "ERROR"
    )
```

</div>

### Attributes

| Attribute      | Type             | Description                           |
|----------------|------------------|---------------------------------------|
| `api_base_url` | str              | Base URL for the API endpoints        |
| `oauth_client` | OAuth2Client     | OAuth2 client handling authentication |
| `session`      | requests.Session | HTTP session for making requests      |
| `logger`       | Logger           | Logger instance for SDK logging       |

### Core Methods

#### Request Methods

<div class="termy">

<!-- termynal -->

```python
def request(self, method: str, endpoint: str, **kwargs)
```

</div>

Makes a generic HTTP request to the API.

**Parameters:**

- `method`: HTTP method (GET, POST, PUT, DELETE)
- `endpoint`: API endpoint path
- `**kwargs`: Additional request parameters

<div class="termy">

<!-- termynal -->

```python
def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs)
```

</div>

Makes a GET request to the specified endpoint.

<div class="termy">

<!-- termynal -->

```python
def post(self, endpoint: str, **kwargs)
```

</div>

Makes a POST request to the specified endpoint.

<div class="termy">

<!-- termynal -->

```python
def put(self, endpoint: str, **kwargs)
```

</div>

Makes a PUT request to the specified endpoint.

<div class="termy">

<!-- termynal -->

```python
def delete(self, endpoint: str, **kwargs)
```

</div>

Makes a DELETE request to the specified endpoint.

## Usage Examples

### Basic Client Initialization

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm

# Initialize client with basic configuration
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    api_base_url="https://api.example.com"
)
```

</div>

### Using Debug Logging

<div class="termy">

<!-- termynal -->

```python
# Initialize with debug logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    api_base_url="https://api.example.com",
    log_level="DEBUG"  # Enable detailed logging
)
```

</div>

### Making API Requests

#### GET Request Example

<div class="termy">

<!-- termynal -->

```python
# List addresses with parameters
response = client.get(
    endpoint="/v1/objects/addresses",
    params={"folder": "Texas", "limit": 100}
)
```

</div>

#### POST Request Example

<div class="termy">

<!-- termynal -->

```python
# Create a new address object
new_address = {
    "name": "example-address",
    "folder": "Texas",
    "ip_netmask": "192.168.1.0/24"
}
response = client.post(
    endpoint="/v1/objects/addresses",
    json=new_address
)
```

</div>

#### PUT Request Example

<div class="termy">

<!-- termynal -->

```python
# Update an existing address
updated_address = {
    "name": "example-address",
    "ip_netmask": "192.168.2.0/24"
}
response = client.put(
    endpoint="/v1/objects/addresses/example-address",
    json=updated_address
)
```

</div>

#### DELETE Request Example

<div class="termy">

<!-- termynal -->

```python
# Delete an address object
response = client.delete(
    endpoint="/v1/objects/addresses/example-address"
)
```

</div>

## Error Handling

### Comprehensive Error Handling Example

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.exceptions import (
    AuthenticationError,
    NotFoundError,
    BadRequestError,
    ServerError,
    APIError
)


def perform_api_operations():
    try:
        # Initialize client
        client = Scm(
            client_id="your_client_id",
            client_secret="your_client_secret",
            tsg_id="your_tsg_id",
            log_level="INFO"
        )

        # Perform API operations
        try:
            # List addresses
            addresses = client.get("/v1/objects/addresses")
            print(f"Found {len(addresses)} addresses")

            # Create new address
            new_address = {
                "name": "test-address",
                "folder": "Texas",
                "ip_netmask": "192.168.1.0/24"
            }
            created = client.post("/v1/objects/addresses", json=new_address)
            print(f"Created address: {created['name']}")

        except AuthenticationError as e:
            print(f"Authentication failed: {e.message}")
            print(f"Error code: {e.error_code}")
            print(f"HTTP status: {e.http_status_code}")

        except NotFoundError as e:
            print(f"Resource not found: {e.message}")
            if e.details:
                print(f"Additional details: {e.details}")

        except BadRequestError as e:
            print(f"Invalid request: {e.message}")
            if e.details:
                print(f"Validation errors: {e.details}")

        except ServerError as e:
            print(f"Server error occurred: {e.message}")
            print(f"Status code: {e.http_status_code}")

    except APIError as e:
        print(f"API error occurred: {e}")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
```

</div>

## Best Practices

### Client Configuration

1. **Logging Configuration**
    - Use appropriate log levels for different environments
    - Set to DEBUG for development and troubleshooting
    - Set to ERROR or WARNING for production

2. **Error Handling**
    - Always wrap API calls in try-except blocks
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting
    - Include proper error recovery mechanisms

3. **Session Management**
    - Reuse client instances when possible
    - Properly close/cleanup sessions when done
    - Handle token refresh scenarios

### Code Examples

#### Reusing Client Instance

<div class="termy">

<!-- termynal -->

```python
# Create a single client instance
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)


# Reuse for multiple operations
def get_address(name: str):
    return client.get(f"/v1/objects/addresses/{name}")


def create_address(address_data: dict):
    return client.post("/v1/objects/addresses", json=address_data)
```

</div>

#### Using with Context Managers

<div class="termy">

<!-- termynal -->

```python
from contextlib import contextmanager


@contextmanager
def scm_client_session(**kwargs):
    client = Scm(**kwargs)
    try:
        yield client
    finally:
        # Cleanup if needed
        pass


# Usage
with scm_client_session(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id"
) as client:
    addresses = client.get("/v1/objects/addresses")
```

</div>

## Common Error Scenarios

### Authentication Failures

- Invalid credentials
- Expired tokens
- Missing required parameters

### Request Failures

- Malformed requests
- Invalid parameters
- Missing required fields
- Resource not found
- Duplicate resources

### Server Errors

- Timeouts
- Service unavailable
- Internal server errors
