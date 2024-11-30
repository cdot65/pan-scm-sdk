# Client Module

## Overview

The SCM (Strata Cloud Manager) client module provides the primary interface for interacting with the Palo Alto Networks
Strata Cloud Manager API. It handles authentication, request management, and provides a clean interface for making API
calls with proper error handling and Pydantic model validation.

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
            api_base_url: str = "https://api.strata.paloaltonetworks.com",
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

Makes a generic HTTP request to the API and returns a Pydantic model or None.

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

Makes a GET request to the specified endpoint, automatically handling token refresh.

<div class="termy">

<!-- termynal -->

```python
def post(self, endpoint: str, **kwargs)
```

</div>

Makes a POST request to the specified endpoint, automatically handling token refresh.

<div class="termy">

<!-- termynal -->

```python
def put(self, endpoint: str, **kwargs)
```

</div>

Makes a PUT request to the specified endpoint, automatically handling token refresh.

<div class="termy">

<!-- termynal -->

```python
def delete(self, endpoint: str, **kwargs)
```

</div>

Makes a DELETE request to the specified endpoint, automatically handling token refresh.

### Job Management Methods

<div class="termy">

<!-- termynal -->

```python
def list_jobs(
        self,
        limit: int = 100,
        offset: int = 0,
        parent_id: Optional[str] = None
) -> JobListResponse
```

</div>

Lists jobs with pagination support and optional parent ID filtering.

<div class="termy">

<!-- termynal -->

```python
def wait_for_job(
        self,
        job_id: str,
        timeout: int = 300,
        poll_interval: int = 10
) -> Optional[JobStatusResponse]
```

</div>

Waits for a job to complete with configurable timeout and polling interval.

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
    tsg_id="your_tsg_id"
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
    endpoint="/config/objects/v1/addresses",
    params={"folder": "Texas", "limit": 100}
)
```

</div>

#### POST Request Example with Pydantic Models

<div class="termy">

<!-- termynal -->

```python
from scm.models.operations import CandidatePushRequestModel

# Create a commit request
commit_request = CandidatePushRequestModel(
    folders=["Texas"],
    admin=["admin@example.com"],
    description="Initial commit"
)

response = client.post(
    endpoint="/config/operations/v1/config-versions/candidate:push",
    json=commit_request.model_dump()
)
```

</div>

#### Commit Changes Example

<div class="termy">

<!-- termynal -->

```python
# Commit changes with synchronous wait
response = client.commit(
    folders=["Texas"],
    description="Configuration update",
    sync=True,
    timeout=300
)

if response.success:
    print(f"Commit successful! Job ID: {response.job_id}")
```

</div>

## Error Handling

### Comprehensive Error Handling Example

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    InvalidObjectError,
    ServerError,
    TimeoutError
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

        try:
            # Commit changes
            response = client.commit(
                folders=["Texas"],
                description="Test commit",
                sync=True
            )
            print(f"Commit job ID: {response.job_id}")

        except AuthenticationError as e:
            print(f"Authentication failed: {e.message}")
            print(f"Error code: {e.error_code}")

        except InvalidObjectError as e:
            print(f"Invalid request data: {e.message}")
            if e.details:
                print(f"Validation errors: {e.details}")

        except TimeoutError as e:
            print(f"Operation timed out: {str(e)}")

        except ServerError as e:
            print(f"Server error occurred: {e.message}")
            print(f"Status code: {e.http_status_code}")

    except APIError as e:
        print(f"API error occurred: {e}")
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

3. **Token Management**

    - The client automatically handles token refresh
    - No manual token management required
    - Tokens are refreshed when expired before requests

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
def commit_changes(folders: List[str], description: str):
    return client.commit(
        folders=folders,
        description=description,
        sync=True
    )


def check_job_status(job_id: str):
    return client.get_job_status(job_id)
```

</div>

## Common Error Scenarios

### Authentication Failures

- Invalid credentials (`AuthenticationError`)
- Expired tokens (handled automatically)
- Missing required parameters (`InvalidObjectError`)

### Request Failures

- Malformed requests (`InvalidObjectError`)
- Invalid parameters (`InvalidObjectError`)
- Resource not found (`NotFoundError`)
- Operation timeouts (`TimeoutError`)

### Server Errors

- Service unavailable (`ServerError`)
- Internal server errors (`ServerError`)
- Gateway timeouts (`GatewayTimeoutError`)