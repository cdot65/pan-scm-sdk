# Client Module

## Overview

The SCM (Strata Cloud Manager) client module provides the primary interface for interacting with the Palo Alto Networks
Strata Cloud Manager API. It handles authentication, request management, and provides a clean interface for making API
calls with proper error handling and Pydantic model validation.

Starting with version 0.3.14, the SCM client supports a unified interface for accessing service objects through attribute-based
access, allowing for a more intuitive and streamlined developer experience.

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

## Client Usage Patterns

The SDK supports two primary usage patterns:

### Unified Client Interface (Recommended)

The unified client approach allows you to access all service objects directly through the client instance, providing a more intuitive and streamlined developer experience:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm

# Initialize client with your credentials
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access services directly through attributes
client.address.create({...})
client.tag.list(folder="Texas")
client.security_rule.get(rule_id)
```

</div>

This pattern offers several advantages:
- Reduced code verbosity
- Centralized client management
- Automatic token refresh handling
- No need to create multiple service instances
- Consistent interface across all services

### Traditional Service Instantiation (Legacy)

You can still use the traditional pattern where service objects are explicitly instantiated:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Address

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create service instance manually
address_service = Address(client)

# Use the service instance
address_service.create({...})
```

</div>

!!! note
    While the traditional pattern is still supported for backward compatibility, it's recommended to use the unified client interface for new development as it provides a more streamlined developer experience and ensures proper token refresh handling.

### Available Services

The unified client provides access to all service objects in the SDK through attributes:

**Objects**
- `client.address` - Address objects
- `client.address_group` - Address Group objects
- `client.application` - Application objects
- `client.application_filters` - Application Filters
- `client.application_group` - Application Group objects
- `client.dynamic_user_group` - Dynamic User Group objects
- `client.external_dynamic_lists` - External Dynamic Lists
- `client.hip_object` - HIP Objects
- `client.hip_profile` - HIP Profiles
- `client.http_server_profiles` - HTTP Server Profiles
- `client.service` - Service objects
- `client.service_group` - Service Group objects
- `client.tag` - Tag objects

**Network**
- `client.nat_rules` - NAT Rules

**Deployment**
- `client.remote_networks` - Remote Networks

**Security**
- `client.security_rule` - Security Rules
- `client.anti_spyware_profile` - Anti-Spyware Profiles
- `client.decryption_profile` - Decryption Profiles
- `client.dns_security_profile` - DNS Security Profiles
- `client.url_categories` - URL Categories
- `client.vulnerability_protection_profile` - Vulnerability Protection Profiles
- `client.wildfire_antivirus_profile` - WildFire Antivirus Profiles

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

### Client Initialization

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

### Using the Unified Client Interface

<div class="termy">

<!-- termynal -->

```python
# Create an address
address_data = {
    "name": "test-address",
    "ip_netmask": "192.168.1.0/24",
    "description": "Test network address",
    "folder": "Texas"
}
new_address = client.address.create(address_data)
print(f"Created address: {new_address.name} with ID: {new_address.id}")

# List tags
tags = client.tag.list(folder="Texas")
for tag in tags:
    print(f"Tag: {tag.name}, Color: {tag.color}")

# Create a security rule
rule_data = {
    "name": "allow-internal",
    "folder": "Texas",
    "source": {"address": ["test-address"]},
    "destination": {"address": ["any"]},
    "application": ["web-browsing"],
    "service": ["application-default"],
    "action": "allow"
}
new_rule = client.security_rule.create(rule_data)
print(f"Created rule: {new_rule.name}")

# Commit changes
result = client.commit(
    folders=["Texas"],
    description="Added test configuration",
    sync=True
)
print(f"Commit job ID: {result.job_id}")
```

</div>

### Making Raw API Requests

For endpoints not yet covered by dedicated service classes:

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

## ScmClient Alias

Starting with version 0.3.14, the SDK also provides an `ScmClient` class as an alias for `Scm`. This class offers the exact
same functionality but with a more explicit name that better describes its purpose:

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Use ScmClient instead of Scm (identical functionality)
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)
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

1. **Use the Unified Client Interface**
    - Leverage the attribute-based access for a cleaner code structure
    - Avoid creating separate service instances
    - Utilize a single client instance for all operations

2. **Client Reuse**
    - Create a single client instance and reuse it
    - Avoid creating multiple client instances

3. **Error Handling**
    - Always wrap API calls in try-except blocks
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

4. **Job Management**
    - Use sync=True for simpler workflows when waiting for job completion
    - Set appropriate timeouts based on operation complexity
    - Monitor child jobs for complex operations

5. **Logging**
    - Use DEBUG level for development and troubleshooting
    - Use ERROR level for production environments