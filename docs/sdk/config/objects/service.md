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
    "folder": "Texas",
    "tag": ["Automation"]
}

new_service = services.create(tcp_service)
print(f"Created service: {new_service.name}")
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
    "folder": "Texas"
}

new_service = services.create(udp_service)
print(f"Created service: {new_service.name}")
```

</div>

## Getting Services

Use the `get()` method to retrieve a service by its ID.

<div class="termy">

<!-- termynal -->

```python
service_id = "123e4567-e89b-12d3-a456-426655440000"
service_obj = service.get(service_id)
print(f"Service: {service_obj.name}")
print(f"Protocol: {'TCP' if 'tcp' in service_obj.protocol else 'UDP'}")
```

</div>

## Updating Services

The `update()` method allows you to modify existing services.

<div class="termy">

<!-- termynal -->

```python
service_object = services.fetch(folder='Texas', name='dns-service')
service_object['description'] = 'updated description'
updated_service = services.update(service_object)
print(f"Updated service: {updated_service.name}")
```

</div>

## Deleting Services

Use the `delete()` method to remove a service.

<div class="termy">

<!-- termynal -->

```python
service_id = "123e4567-e89b-12d3-a456-426655440000"
services.delete(service_id)
print("Service deleted successfully")
```

</div>

## Listing Services

The `list()` method retrieves multiple services with optional filtering. You can filter the results using the
following kwargs:

- `protocol`: List[str] - Filter by protocol type (e.g., ['tcp', 'udp'])
- `tag`: List[str] - Filter by tags (e.g., ['Automation', 'Production'])

<div class="termy">

<!-- termynal -->

```python
# List all services in a folder
services = services.list(folder="Texas")

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
for svc in services:
    print(f"Name: {svc.name}")
    if svc.protocol.tcp:
        print(f"TCP Ports: {svc.protocol.tcp.port}")
    elif svc.protocol.udp:
        print(f"UDP Ports: {svc.protocol.udp.port}")
```

</div>

## Fetching Services

The `fetch()` method retrieves a single service by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
service_obj = services.fetch(name="web-service", folder="Texas")
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
services = Service(client)

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
fetched_service = services.fetch(
    name="test-service",
    folder="Texas"
)

# Modify the fetched service
fetched_service["description"] = "Updated test service"
fetched_service["protocol"]["tcp"]["port"] = "8080,8443"

# Update using the modified object
updated_service = services.update(fetched_service)
print(f"Updated service: {updated_service.name}")
print(f"New ports: {updated_service.protocol.tcp.port}")

# List all services
services = services.list(folder="Texas")
for svc in services:
    print(f"Listed service: {svc.name}")

# Clean up
services.delete(new_service.id)
print("Service deleted successfully")
```

</div>

## Related Models

- [ServiceCreateModel](../../models/objects/service_models.md#servicecreatemodel)
- [ServiceUpdateModel](../../models/objects/service_models.md#serviceupdatemodel)
- [ServiceResponseModel](../../models/objects/service_models.md#serviceresponsemodel)