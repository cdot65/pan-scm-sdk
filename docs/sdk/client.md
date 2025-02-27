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

#### HTTP Methods

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

Lists jobs with pagination support and optional parent ID filtering. When parent_id is provided, returns only child jobs
of the specified parent job.

<div class="termy">

<!-- termynal -->

```python
def get_job_status(self, job_id: str) -> JobStatusResponse
```

</div>

Gets the status of a specific job.

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

### Configuration Management Methods

<div class="termy">

<!-- termynal -->

```python
def commit(
        self,
        folders: List[str],
        description: str,
        admin: Optional[List[str]] = None,
        sync: bool = False,
        timeout: int = 300,
) -> CandidatePushResponseModel
```

</div>

Commits configuration changes to SCM with options for synchronous waiting and custom timeout.

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

### Making API Requests

Please consider using the dedicated class objects for making API requests to specific configuration objects, but if
there is no existing class object, you can use the `request()` method directly to get your job done until coverage has
improved.

<div class="termy">

<!-- termynal -->

```python
# List objects with parameters
response = client.get(
    endpoint="/config/objects/v1/addresses",
    params={"folder": "Texas", "limit": 100}
)

# Create new object
response = client.post(
    endpoint="/config/objects/v1/addresses",
    json={
        "name": "test-address",
        "ip_netmask": "192.168.1.0/24",
        "folder": "Texas"
    }
)
```

</div>

### Job Management

<div class="termy">

<!-- termynal -->

```python
# List recent jobs
jobs = client.list_jobs(limit=10)

# Get child jobs of a specific job
child_jobs = client.list_jobs(parent_id="parent-job-id")

# Wait for job completion
status = client.wait_for_job("job-id", timeout=600)
```

</div>

### Committing Changes

<div class="termy">

<!-- termynal -->

```python
# Commit changes synchronously
result = client.commit(
    folders=["Texas"],
    admin=["all"],
    description="Update network configuration",
    sync=True,
    timeout=300
)

print(f"Commit job ID: {result.job_id}")

# Check commit status
status = client.get_job_status(result.job_id)
print(f"Status: {status.data[0].status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.exceptions import APIError, AuthenticationError, TimeoutError

try:
    result = client.commit(
        folders=["Texas"],
        admin=["automation@scm-tenant.example.com"],
        description="Update configuration",
        sync=True
    )
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except TimeoutError as e:
    print(f"Operation timed out: {str(e)}")
except APIError as e:
    print(f"API error: {str(e)}")
```

</div>

## Best Practices

1. **Client Reuse**
    - Create a single client instance and reuse it
    - Avoid creating multiple client instances

2. **Error Handling**
    - Always wrap API calls in try-except blocks
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

3. **Job Management**
    - Use sync=True for simpler workflows when waiting for job completion
    - Set appropriate timeouts based on operation complexity
    - Monitor child jobs for complex operations

4. **Logging**
    - Use DEBUG level for development and troubleshooting
    - Use ERROR level for production environments