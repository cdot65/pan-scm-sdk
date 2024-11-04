# Service Configuration Object

The `Service` class provides functionality to manage service objects in Palo Alto Networks' Strata Cloud Manager.
Services
define network protocols and ports that can be referenced in security policies and NAT rules.

## Overview

Services in Strata Cloud Manager allow you to:

- Define TCP and UDP services with specific ports
- Configure protocol timeout overrides
- Organize services within folders, snippets, or devices
- Apply tags for better organization
- Reference services in security policies and other configurations

## Methods

| Method     | Description                            |
|------------|----------------------------------------|
| `create()` | Creates a new service                  |
| `get()`    | Retrieves a service by ID              |
| `update()` | Updates an existing service            |
| `delete()` | Deletes a service                      |
| `list()`   | Lists services with optional filtering |
| `fetch()`  | Retrieves a single service by name     |

## Creating Services

The `create()` method allows you to define new services. You must specify exactly one protocol type (TCP or UDP) and one
container type (folder, snippet, or device).

**Example: Creating a TCP Service**

<div class="termy">

<!-- termynal -->

```python
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
    "folder": "Shared",
    "tag": ["web"]
}

new_service = service.create(tcp_service)
print(f"Created service: {new_service['name']}")
```

</div>

**Example: Creating a UDP Service**

<div class="termy">

<!-- termynal -->

```python
udp_service = {
    "name": "dns-service",
    "protocol": {
        "udp": {
            "port": "53"
        }
    },
    "description": "DNS service",
    "folder": "Shared"
}

new_service = service.create(udp_service)
print(f"Created service: {new_service['name']}")
```

</div>

## Getting Services

Use the `get()` method to retrieve a service by its ID.

<div class="termy">

<!-- termynal -->

```python
service_id = "123e4567-e89b-12d3-a456-426655440000"
service_obj = service.get(service_id)
print(f"Service: {service_obj['name']}")
print(f"Protocol: {'TCP' if 'tcp' in service_obj['protocol'] else 'UDP'}")
```

</div>

## Updating Services

The `update()` method allows you to modify existing services.

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "description": "Updated web service",
    "protocol": {
        "tcp": {
            "port": "80,443,8080",
            "override": {
                "timeout": 120
            }
        }
    }
}

updated_service = service.update(update_data)
print(f"Updated service: {updated_service['name']}")
```

</div>

## Deleting Services

Use the `delete()` method to remove a service.

<div class="termy">

<!-- termynal -->

```python
service_id = "123e4567-e89b-12d3-a456-426655440000"
service.delete(service_id)
print("Service deleted successfully")
```

</div>

## Listing Services

The `list()` method retrieves multiple services with optional filtering.

<div class="termy">

<!-- termynal -->

```python
# List all services in a folder
services = service.list(folder="Shared")
for svc in services:
    print(f"Name: {svc['name']}")

# List with specific filters
filtered_services = service.list(
    folder="Shared",
    names=["web-service", "dns-service"],
    tags=["web"]
)
for svc in filtered_services:
    print(f"Filtered service: {svc['name']}")
```

</div>

## Fetching Services

The `fetch()` method retrieves a single service by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
service_obj = service.fetch(
    name="web-service",
    folder="Shared"
)
print(f"Found service: {service_obj['name']}")
print(f"Current ports: {service_obj['protocol']['tcp']['port']}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a service:

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

# Initialize service object
service = Service(client)

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
    "folder": "Shared"
}

new_service = service.create(create_data)
print(f"Created service: {new_service['name']}")

# Fetch the service by name
fetched_service = service.fetch(
    name="test-service",
    folder="Shared"
)

# Modify the fetched service
fetched_service["description"] = "Updated test service"
fetched_service["protocol"]["tcp"]["port"] = "8080,8443"

# Update using the modified object
updated_service = service.update(fetched_service)
print(f"Updated service: {updated_service['name']}")
print(f"New ports: {updated_service['protocol']['tcp']['port']}")

# List all services
services = service.list(folder="Shared")
for svc in services:
    print(f"Listed service: {svc['name']}")

# Clean up
service.delete(new_service['id'])
print("Service deleted successfully")
```

</div>

## Related Models

- [ServiceCreateModel](../../models/objects/service_models.md#servicecreatemodel)
- [ServiceUpdateModel](../../models/objects/service_models.md#serviceupdatemodel)
- [ServiceResponseModel](../../models/objects/service_models.md#serviceresponsemodel)