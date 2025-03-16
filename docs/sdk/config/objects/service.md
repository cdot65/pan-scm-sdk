# Service Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Service Model Attributes](#service-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Services](#creating-services)
    - [Retrieving Services](#retrieving-services)
    - [Updating Services](#updating-services)
    - [Listing Services](#listing-services)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Services](#deleting-services)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `Service` class provides functionality to manage service objects in Palo Alto Networks' Strata Cloud Manager. This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting service
definitions that specify network protocols and ports for use in security policies.

## Core Methods

| Method     | Description                    | Parameters                    | Return Type                  |
|------------|--------------------------------|-------------------------------|------------------------------|
| `create()` | Creates a new service          | `data: Dict[str, Any]`        | `ServiceResponseModel`       |
| `get()`    | Retrieves a service by ID      | `object_id: str`              | `ServiceResponseModel`       |
| `update()` | Updates an existing service    | `service: ServiceUpdateModel` | `ServiceResponseModel`       |
| `delete()` | Deletes a service              | `object_id: str`              | `None`                       |
| `list()`   | Lists services with filtering  | `folder: str`, `**filters`    | `List[ServiceResponseModel]` |
| `fetch()`  | Gets service by name/container | `name: str`, `folder: str`    | `ServiceResponseModel`       |

## Service Model Attributes

| Attribute      | Type        | Required     | Description                                 |
|----------------|-------------|--------------|---------------------------------------------|
| `name`         | str         | Yes          | Name of service (max 63 chars)              |
| `id`           | UUID        | Yes*         | Unique identifier (*response only)          |
| `protocol`     | Protocol    | Yes          | Protocol configuration (TCP/UDP)            |
| `protocol.tcp` | TCPProtocol | One Required | TCP protocol settings                       |
| `protocol.udp` | UDPProtocol | One Required | UDP protocol settings                       |
| `description`  | str         | No           | Description (max 1023 chars)                |
| `tag`          | List[str]   | No           | List of tags                                |
| `folder`       | str         | Yes**        | Folder location (**one container required)  |
| `snippet`      | str         | Yes**        | Snippet location (**one container required) |
| `device`       | str         | Yes**        | Device location (**one container required)  |

### Protocol Override Settings

| Attribute           | Type | Required | Description                  |
|---------------------|------|----------|------------------------------|
| `timeout`           | int  | No       | Connection timeout (seconds) |
| `halfclose_timeout` | int  | No       | Half-close timeout (seconds) |
| `timewait_timeout`  | int  | No       | Time-wait timeout (seconds)  |

## Exceptions

| Exception                    | HTTP Code | Description                    |
|------------------------------|-----------|--------------------------------|
| `InvalidObjectError`         | 400       | Invalid service data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters    |
| `NameNotUniqueError`         | 409       | Service name already exists    |
| `ObjectNotPresentError`      | 404       | Service not found              |
| `ReferenceNotZeroError`      | 409       | Service still referenced       |
| `AuthenticationError`        | 401       | Authentication failed          |
| `ServerError`                | 500       | Internal server error          |

## Basic Configuration

The Service service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Service service directly through the client
# No need to create a separate Service instance
services = client.service
```

</div>

### Traditional Service Instantiation (Legacy)

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Service

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Service object explicitly
services = Service(client)
```

</div>

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Services

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# TCP service configuration
tcp_service = {
    "name": "web-service",
    "protocol": {
        "tcp": {
            "port": "80,443",
            "override": {
                "timeout": 60,
                "halfclose_timeout": 30
            }
        }
    },
    "description": "Web service ports",
    "folder": "Texas",
    "tag": ["Web", "Production"]
}

# Create TCP service
tcp_service_obj = client.service.create(tcp_service)

# UDP service configuration
udp_service = {
    "name": "dns-service",
    "protocol": {
        "udp": {
            "port": "53",
            "override": {
                "timeout": 30
            }
        }
    },
    "description": "DNS service",
    "folder": "Texas",
    "tag": ["DNS"]
}

# Create UDP service
udp_service_obj = client.service.create(udp_service)
```

</div>

### Retrieving Services

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
service = client.service.fetch(name="web-service", folder="Texas")
print(f"Found service: {service.name}")

# Get by ID
service_by_id = client.service.get(service.id)
print(f"Protocol: {'TCP' if service_by_id.protocol.tcp else 'UDP'}")
if service_by_id.protocol.tcp:
    print(f"Ports: {service_by_id.protocol.tcp.port}")
```

</div>

### Updating Services

<div class="termy">

<!-- termynal -->

```python
# Fetch existing service
existing_service = client.service.fetch(name="web-service", folder="Texas")

# Update ports and timeouts
if existing_service.protocol.tcp:
    existing_service.protocol.tcp.port = "80,443,8443"
    existing_service.protocol.tcp.override.timeout = 120

# Update description and tags
existing_service.description = "Updated web service ports"
existing_service.tag = ["Web", "Production", "Updated"]

# Perform update
updated_service = client.service.update(existing_service)
```

</div>

### Listing Services

<div class="termy">

<!-- termynal -->

```python
# Pass filters directly into the list method
filtered_services = client.service.list(
    folder='Texas',
    protocols=['tcp'],
    tags=['Production']
)

# Process results
for svc in filtered_services:
    print(f"Name: {svc.name}")
    if svc.protocol.tcp:
        print(f"TCP Ports: {svc.protocol.tcp.port}")
    elif svc.protocol.udp:
        print(f"UDP Ports: {svc.protocol.udp.port}")

# Define filter parameters as a dictionary
list_params = {
    "folder": "Texas",
    "protocols": ["udp"],
    "tags": ["DNS"]
}

# List services with filters as kwargs
filtered_services = client.service.list(**list_params)
```

</div>

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `types`, `values`, and `tags`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

<div class="termy">

<!-- termynal -->

```python
# Only return services defined exactly in 'Texas'
exact_services = client.service.list(
   folder='Texas',
   exact_match=True
)

for svc in exact_services:
   print(f"Exact match: {svc.name} in {svc.folder}")

# Exclude all services from the 'All' folder
no_all_services = client.service.list(
   folder='Texas',
   exclude_folders=['All']
)

for svc in no_all_services:
   assert svc.folder != 'All'
   print(f"Filtered out 'All': {svc.name}")

# Exclude services that come from 'default' snippet
no_default_snippet = client.service.list(
   folder='Texas',
   exclude_snippets=['default']
)

for svc in no_default_snippet:
   assert svc.snippet != 'default'
   print(f"Filtered out 'default' snippet: {svc.name}")

# Exclude services associated with 'DeviceA'
no_deviceA = client.service.list(
   folder='Texas',
   exclude_devices=['DeviceA']
)

for svc in no_deviceA:
   assert svc.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {svc.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.service.list(
   folder='Texas',
   exact_match=True,
   exclude_folders=['All'],
   exclude_snippets=['default'],
   exclude_devices=['DeviceA']
)

for svc in combined_filters:
   print(f"Combined filters result: {svc.name} in {svc.folder}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient
from scm.config.objects import Service

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom Service instance with max_limit
service_service = Service(client, max_limit=4321)
all_services1 = service_service.list(folder='Texas')

# Option 2: Use the unified client interface directly
# This will use the default max_limit (2500)
all_services2 = client.service.list(folder='Texas')

# Both options will auto-paginate through all available objects.
# The services are fetched in chunks according to the max_limit.
```

</div>

### Deleting Services

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
service_id = "123e4567-e89b-12d3-a456-426655440000"
client.service.delete(service_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated service definitions",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Create service configuration
    service_config = {
        "name": "test-service",
        "protocol": {
            "tcp": {
                "port": "8080",
                "override": {
                    "timeout": 30
                }
            }
        },
        "folder": "Texas",
        "description": "Test service",
        "tag": ["Test"]
    }

    # Create the service using the unified client interface
    new_service = client.service.create(service_config)

    # Commit changes directly from the client
    result = client.commit(
        folders=["Texas"],
        description="Added test service",
        sync=True
    )

    # Check job status directly from the client
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid service data: {e.message}")
except NameNotUniqueError as e:
    print(f"Service name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Service not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Service still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.service`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Protocol Configuration**
    - Define clear port ranges
    - Use appropriate timeouts
    - Document protocol choices
    - Consider service dependencies
    - Validate port conflicts

3. **Container Management**
    - Always specify exactly one container
    - Use consistent container names
    - Validate container existence
    - Group related services

4. **Error Handling**
    - Validate input data
    - Handle specific exceptions
    - Log error details
    - Monitor commit status
    - Track job completion

5. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed services
    - Implement proper retry logic
    - Monitor timeout settings

6. **Security**
    - Follow least privilege principle
    - Validate port ranges
    - Document security implications
    - Monitor service usage
    - Track policy references

## Full Script Examples

Refer to
the [service.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/service.py).

## Related Models

- [ServiceCreateModel](../../models/objects/service_models.md#Overview)
- [ServiceUpdateModel](../../models/objects/service_models.md#Overview)
- [ServiceResponseModel](../../models/objects/service_models.md#Overview)
