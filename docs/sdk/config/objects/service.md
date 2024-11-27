# Service Configuration Object

The `Service` class provides functionality to manage service objects in Palo Alto Networks' Strata Cloud Manager.
Services define network protocols and ports that can be referenced in security policies and NAT rules.

## Overview

Services in Strata Cloud Manager allow you to:

- Define TCP and UDP services with specific ports
- Configure protocol timeout overrides
- Organize services within folders, snippets, or devices
- Apply tags for better organization
- Reference services in security policies and other configurations

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during service object
management.

## Methods

| Method     | Description                            |
|------------|----------------------------------------|
| `create()` | Creates a new service                  |
| `get()`    | Retrieves a service by ID              |
| `update()` | Updates an existing service            |
| `delete()` | Deletes a service                      |
| `list()`   | Lists services with optional filtering |
| `fetch()`  | Retrieves a single service by name     |

## Exceptions

The SDK uses a hierarchical exception system for error handling:

### Client Errors (4xx)

- `InvalidObjectError`: Raised when service object data is invalid or malformed
- `MissingQueryParameterError`: Raised when required parameters (folder, name) are empty
- `NotFoundError`: Raised when a service doesn't exist
- `AuthenticationError`: Raised for authentication failures
- `AuthorizationError`: Raised for permission issues
- `ConflictError`: Raised when service names conflict
- `NameNotUniqueError`: Raised when creating duplicate service names
- `ReferenceNotZeroError`: Raised when deleting services still referenced by policies

### Server Errors (5xx)

- `ServerError`: Base class for server-side errors
- `APINotImplementedError`: When API endpoint isn't implemented
- `GatewayTimeoutError`: When request times out
- `SessionTimeoutError`: When the API session times out

## Creating Services

The `create()` method allows you to create new services with proper error handling.

**Example: Creating a TCP Service**

<div class="termy">

```python
from scm.client import Scm
from scm.config.objects import Service
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

services = Service(client)

try:
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
        "description": "Web service for HTTP/HTTPS",
        "folder": "Texas",
        "tag": ["Automation"]
    }

    new_service = services.create(tcp_service)
    print(f"Created service: {new_service.name}")

except NameNotUniqueError as e:
    print(f"Service name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid service data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

**Example: Creating a UDP Service**

<div class="termy">

```python
try:
    udp_service = {
        "name": "dns-service",
        "protocol": {
            "udp": {
                "port": "53"
            }
        },
        "description": "DNS service",
        "folder": "Texas"
    }

    new_service = services.create(udp_service)
    print(f"Created service: {new_service.name}")

except InvalidObjectError as e:
    print(f"Invalid service data: {e.message}")
    print(f"Error code: {e.error_code}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting Services

Use the `get()` method to retrieve a service by its ID.

<div class="termy">

```python
try:
    service_id = "123e4567-e89b-12d3-a456-426655440000"
    service_obj = services.get(service_id)
    print(f"Service: {service_obj.name}")
    print(f"Protocol: {'TCP' if 'tcp' in service_obj.protocol else 'UDP'}")

except NotFoundError as e:
    print(f"Service not found: {e.message}")
```

</div>

## Updating Services

The `update()` method allows you to modify existing services.

<div class="termy">

```python
try:
    service_object = services.fetch(folder='Texas', name='dns-service')
    service_object['description'] = 'updated description'
    updated_service = services.update(service_object)
    print(f"Updated service: {updated_service.name}")

except NotFoundError as e:
    print(f"Service not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting Services

Use the `delete()` method to remove a service.

<div class="termy">

```python
try:
    service_id = "123e4567-e89b-12d3-a456-426655440000"
    services.delete(service_id)
    print("Service deleted successfully")

except NotFoundError as e:
    print(f"Service not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Service still in use: {e.message}")
```

</div>

## Listing Services

The `list()` method retrieves multiple services with optional filtering. You can filter the results using the
following kwargs:

- `protocol`: List[str] - Filter by protocol type (e.g., ['tcp', 'udp'])
- `tag`: List[str] - Filter by tags (e.g., ['Automation', 'Production'])

<div class="termy">

```python
try:
    # List all services in a folder
    all_services = services.list(folder="Texas")

    # List only TCP services
    tcp_services = services.list(
        folder="Texas",
        protocol=['tcp']
    )

    # List services with specific tags
    tagged_services = services.list(
        folder="Texas",
        tag=['Automation']
    )

    # Combine multiple filters
    filtered_services = services.list(
        folder="Texas",
        protocol=['tcp'],
        tag=['Production']
    )

    # Print the results
    for svc in all_services:
        print(f"Name: {svc.name}")
        if svc.protocol.tcp:
            print(f"TCP Ports: {svc.protocol.tcp.port}")
        elif svc.protocol.udp:
            print(f"UDP Ports: {svc.protocol.udp.port}")

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching Services

The `fetch()` method retrieves a single service by name from a specific container.

<div class="termy">

```python
try:
    service_obj = services.fetch(name="web-service", folder="Texas")
    print(f"Found service: {service_obj['name']}")
    print(f"Current ports: {service_obj['protocol']['tcp']['port']}")

except NotFoundError as e:
    print(f"Service not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a service with proper error handling:

<div class="termy">

```python
from scm.client import Scm
from scm.config.objects import Service
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
    ReferenceNotZeroError
)

try:
    # Initialize client with debug logging
    client = Scm(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id",
        log_level="DEBUG"  # Enable detailed logging
    )

    # Initialize service object
    services = Service(client)

    try:
        # Create new service
        create_data = {
            "name": "test-service",
            "protocol": {
                "tcp": {
                    "port": "8080",
                    "override": {
                        "timeout": 30
                    }
                }
            },
            "description": "Test service",
            "folder": "Texas"
        }

        new_service = services.create(create_data)
        print(f"Created service: {new_service.name}")

        # Fetch the service by name
        try:
            fetched_service = services.fetch(
                name="test-service",
                folder="Texas"
            )
            print(f"Found service: {fetched_service['name']}")

            # Update the service
            fetched_service["description"] = "Updated test service"
            fetched_service["protocol"]["tcp"]["port"] = "8080,8443"
            updated_service = services.update(fetched_service)
            print(f"Updated ports: {updated_service.protocol.tcp.port}")

        except NotFoundError as e:
            print(f"Service not found: {e.message}")

        # Clean up
        try:
            services.delete(new_service.id)
            print("Service deleted successfully")
        except ReferenceNotZeroError as e:
            print(f"Cannot delete service - still in use: {e.message}")

    except NameNotUniqueError as e:
        print(f"Service name conflict: {e.message}")
    except InvalidObjectError as e:
        print(f"Invalid service data: {e.message}")
        if e.details:
            print(f"Details: {e.details}")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Status code: {e.http_status_code}")
```

</div>

## Full script examples

Refer to the [examples](../../../../examples/scm/config/objects) directory.

## Related Models

- [ServiceCreateModel](../../models/objects/service_models.md#Overview)
- [ServiceUpdateModel](../../models/objects/service_models.md#Overview)
- [ServiceResponseModel](../../models/objects/service_models.md#Overview)