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

# Initialize Service object
services = Service(client)
```

</div>

## Usage Examples

### Creating Services

<div class="termy">

<!-- termynal -->

```python
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
tcp_service_obj = services.create(tcp_service)

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
udp_service_obj = services.create(udp_service)
```

</div>

### Retrieving Services

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
service = services.fetch(name="web-service", folder="Texas")
print(f"Found service: {service.name}")

# Get by ID
service_by_id = services.get(service.id)
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
existing_service = services.fetch(name="web-service", folder="Texas")

# Update ports and timeouts
if existing_service.protocol.tcp:
    existing_service.protocol.tcp.port = "80,443,8443"
    existing_service.protocol.tcp.override.timeout = 120

# Update description and tags
existing_service.description = "Updated web service ports"
existing_service.tag = ["Web", "Production", "Updated"]

# Perform update
updated_service = services.update(existing_service)
```

</div>

### Listing Services

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_services = services.list(
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

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "protocols": ["udp"],
    "tags": ["DNS"]
}

# List with filters as kwargs
filtered_services = services.list(**list_params)
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
exact_services = services.list(
   folder='Texas',
   exact_match=True
)

for app in exact_services:
   print(f"Exact match: {app.name} in {app.folder}")

# Exclude all services from the 'All' folder
no_all_services = services.list(
   folder='Texas',
   exclude_folders=['All']
)

for app in no_all_services:
   assert app.folder != 'All'
   print(f"Filtered out 'All': {app.name}")

# Exclude services that come from 'default' snippet
no_default_snippet = services.list(
   folder='Texas',
   exclude_snippets=['default']
)

for app in no_default_snippet:
   assert app.snippet != 'default'
   print(f"Filtered out 'default' snippet: {app.name}")

# Exclude services associated with 'DeviceA'
no_deviceA = services.list(
   folder='Texas',
   exclude_devices=['DeviceA']
)

for app in no_deviceA:
   assert app.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {app.name}")

# Combine exact_match with multiple exclusions
combined_filters = services.list(
   folder='Texas',
   exact_match=True,
   exclude_folders=['All'],
   exclude_snippets=['default'],
   exclude_devices=['DeviceA']
)

for app in combined_filters:
   print(f"Combined filters result: {app.name} in {app.folder}")
```

### Deleting Services

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
service_id = "123e4567-e89b-12d3-a456-426655440000"
services.delete(service_id)
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

# Commit the changes
result = services.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = services.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = services.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
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

    # Create the service
    new_service = services.create(service_config)

    # Commit changes
    result = services.commit(
        folders=["Texas"],
        description="Added test service",
        sync=True
    )

    # Check job status
    status = services.get_job_status(result.job_id)

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

1. **Protocol Configuration**
    - Define clear port ranges
    - Use appropriate timeouts
    - Document protocol choices
    - Consider service dependencies
    - Validate port conflicts

2. **Container Management**
    - Always specify exactly one container
    - Use consistent container names
    - Validate container existence
    - Group related services

3. **Error Handling**
    - Validate input data
    - Handle specific exceptions
    - Log error details
    - Monitor commit status
    - Track job completion

4. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed services
    - Implement proper retry logic
    - Monitor timeout settings

5. **Security**
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