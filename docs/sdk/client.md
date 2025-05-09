# Client Module

## Overview

The SCM (Strata Cloud Manager) client module provides the primary interface for interacting with the Palo Alto Networks
Strata Cloud Manager API. It handles authentication, request management, and provides a clean interface for making API
calls with proper error handling and Pydantic model validation.

Starting with version 0.3.14, the SCM client supports a unified interface for accessing service objects through attribute-based
access, allowing for a more intuitive and streamlined developer experience.

## SCM Client

### Class Definition

```python
class Scm:
    def __init__(
            self,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            tsg_id: Optional[str] = None,
            api_base_url: str = "https://api.strata.paloaltonetworks.com",
            token_url: str = "https://auth.apps.paloaltonetworks.com/am/oauth2/access_token",
            log_level: str = "ERROR",
            access_token: Optional[str] = None
    )
```

### Attributes

| Attribute      | Type             | Description                           |
|----------------|------------------|---------------------------------------|
| `api_base_url` | str              | Base URL for the API endpoints        |
| `token_url`    | str              | URL for obtaining OAuth tokens        |
| `oauth_client` | OAuth2Client     | OAuth2 client handling authentication |
| `session`      | requests.Session | HTTP session for making requests      |
| `logger`       | Logger           | Logger instance for SDK logging       |

## Authentication Methods

The SDK supports two authentication methods:

### 1. OAuth2 Client Credentials Flow (Standard)

This is the primary authentication method using client credentials:

```python
from scm.client import Scm

# Initialize client with OAuth2 client credentials
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    # Optional parameters:
    # token_url="https://custom.auth.server.com/oauth2/token"
)
```

### 2. Bearer Token Authentication

For scenarios where you already have a valid OAuth token, you can use it directly:

```python
from scm.client import Scm

# Initialize client with a pre-acquired bearer token
client = Scm(
    access_token="your_bearer_token"
    # Optional parameters:
    # api_base_url="https://api.custom-domain.com"
)
```

!!! note
    When using bearer token authentication, token refresh is the caller's responsibility. The SDK will use the token as-is.

!!! warning
    For commit operations with bearer token authentication, you must explicitly provide the `admin` parameter:
    ```python
    # When using bearer token authentication with commit operations
    client.commit(
        folders=["Texas"],
        description="Configuration changes",
        admin=["admin@example.com"],  # Required when using bearer token
        sync=True
    )
    ```

## Client Usage Patterns

The SDK supports two primary usage patterns:

### Unified Client Interface (Recommended)

The unified client approach allows you to access all service objects directly through the client instance, providing a more intuitive and streamlined developer experience:

```python
from scm.client import Scm

# Initialize client with your preferred authentication method
# Option 1: OAuth2 client credentials
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Option 2: Bearer token
# client = Scm(access_token="your_bearer_token")

# Access services directly through attributes
client.address.create({...})
client.tag.list(folder="Texas")
client.security_rule.get(rule_id)
```

This pattern offers several advantages:
- Reduced code verbosity
- Centralized client management
- Automatic token refresh handling
- No need to create multiple service instances
- Consistent interface across all services

### Traditional Service Instantiation (Legacy)

You can still use the traditional pattern where service objects are explicitly instantiated:

```python
from scm.client import Scm
from scm.config.objects import Address

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    # Optional parameters:
    # token_url="https://custom.auth.server.com/oauth2/token"
)

# Create service instance manually
address_service = Address(client)

# Use the service instance
address_service.create({...})
```

!!! note
    While the traditional pattern is still supported for backward compatibility, it's recommended to use the unified client interface for new development as it provides a more streamlined developer experience and ensures proper token refresh handling.

### Available Services

The unified client provides access to all service objects in the SDK through attributes. The attribute names match the singular form used in the codebase (e.g., `client.address` not `addresses`):

**Objects**

- `client.address` - IP addresses, CIDR ranges, and FQDNs for security policies
- `client.address_group` - Static or dynamic collections of address objects
- `client.application` - Custom application definitions and signatures
- `client.application_filter` - Filters for identifying applications by characteristics
- `client.application_group` - Logical groups of applications for policy application
- `client.dynamic_user_group` - User groups with dynamic membership criteria
- `client.external_dynamic_list` - Externally managed lists of IPs, URLs, or domains
- `client.hip_object` - Host information profile match criteria
- `client.hip_profile` - Endpoint security compliance profiles
- `client.http_server_profile` - HTTP server configurations for logging and monitoring
- `client.log_forwarding_profile` - Configurations for forwarding logs to external systems
- `client.quarantined_device` - Management of devices blocked from network access
- `client.region` - Geographic regions for policy control
- `client.schedule` - Time-based policies and access control
- `client.service` - Protocol and port definitions for network services
- `client.service_group` - Collections of services for simplified policy management
- `client.syslog_server_profile` - Syslog server configurations for centralized logging
- `client.tag` - Resource classification and organization labels

**Network**

- `client.ike_crypto_profile` - IKE crypto profiles for VPN tunnels
- `client.ike_gateway` - IKE gateway configurations for VPN tunnel endpoints
- `client.ipsec_crypto_profile` - IPsec crypto profiles for VPN tunnel encryption
- `client.nat_rule` - Network address translation policies for traffic routing
- `client.security_zone` - Security zones for network segmentation

**Security**

- `client.anti_spyware_profile` - Protection against spyware, C2 traffic, and data exfiltration
- `client.decryption_profile` - SSL/TLS traffic inspection configurations
- `client.dns_security_profile` - Protection against DNS-based threats and tunneling
- `client.security_rule` - Core security policies controlling network traffic
- `client.url_category` - Custom URL categorization for web filtering
- `client.vulnerability_protection_profile` - Defense against known CVEs and exploit attempts
- `client.wildfire_antivirus_profile` - Cloud-based malware analysis and zero-day protection

**Deployment**

- `client.bandwidth_allocation` - Bandwidth allocation settings for regions and service nodes
- `client.bgp_routing` - BGP routing configuration for cloud connectivity
- `client.internal_dns_server` - DNS server configurations for domain resolution
- `client.network_location` - Geographic network locations for service connectivity
- `client.remote_network` - Secure branch and remote site connectivity configurations
- `client.service_connection` - Service connections to cloud service providers

**Mobile Agent**

- `client.agent_version` - GlobalProtect agent version information
- `client.auth_setting` - Authentication settings for mobile agents

**Setup**

- `client.folder` - Configuration folder management

### Core Methods

#### HTTP Methods

```python
def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs)
```

Makes a GET request to the specified endpoint, automatically handling token refresh.

```python
def post(self, endpoint: str, **kwargs)
```

Makes a POST request to the specified endpoint, automatically handling token refresh.

```python
def put(self, endpoint: str, **kwargs)
```

Makes a PUT request to the specified endpoint, automatically handling token refresh.

```python
def delete(self, endpoint: str, **kwargs)
```

Makes a DELETE request to the specified endpoint, automatically handling token refresh.

### Job Management Methods

```python
def list_jobs(
        self,
        limit: int = 100,
        offset: int = 0,
        parent_id: Optional[str] = None
) -> JobListResponse
```

Lists jobs with pagination support and optional parent ID filtering. When parent_id is provided, returns only child jobs
of the specified parent job.

```python
def get_job_status(self, job_id: str) -> JobStatusResponse
```

Gets the status of a specific job.

```python
def wait_for_job(
        self,
        job_id: str,
        timeout: int = 300,
        poll_interval: int = 10
) -> Optional[JobStatusResponse]
```

Waits for a job to complete with configurable timeout and polling interval.

### Configuration Management Methods

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

Commits configuration changes to SCM with options for synchronous waiting and custom timeout.

## Usage Examples

### Client Initialization

```python
from scm.client import Scm

# Initialize client with OAuth2 client credentials (standard method)
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    # Optional parameters:
    # api_base_url="https://api.custom-domain.com",  # Custom API endpoint
    # token_url="https://auth.custom-domain.com/oauth2/token",  # Custom token endpoint
    # log_level="DEBUG"  # Change logging level
)

# OR initialize client with a bearer token
bearer_client = Scm(
    access_token="your_bearer_token",
    # Optional parameters:
    # api_base_url="https://api.custom-domain.com",  # Custom API endpoint
    # log_level="DEBUG"  # Change logging level
)
```

### Using the Unified Client Interface

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

### Making Raw API Requests

For endpoints not yet covered by dedicated service classes:

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

### Job Management

```python
# List recent jobs
jobs = client.list_jobs(limit=10)

# Get child jobs of a specific job
child_jobs = client.list_jobs(parent_id="parent-job-id")

# Wait for job completion
status = client.wait_for_job("job-id", timeout=600)
```

### Committing Changes

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

## ScmClient Alias

Starting with version 0.3.14, the SDK also provides an `ScmClient` class as an alias for `Scm`. This class offers the exact
same functionality but with a more explicit name that better describes its purpose:

```python
from scm.client import ScmClient

# Use ScmClient instead of Scm with OAuth2 client credentials (identical functionality)
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    # Optional parameters:
    # token_url="https://custom.auth.server.com/oauth2/token"
)

# OR use ScmClient with bearer token authentication
bearer_client = ScmClient(
    access_token="your_bearer_token"
)
```

## Error Handling

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
