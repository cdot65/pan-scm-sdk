# Service Configuration Object

The `Service` class is used to manage service objects in the Strata Cloud Manager. It provides methods to create,
retrieve, update, delete, and list service objects.

---

## Importing the Service Class

<div class="termy">

<!-- termynal -->

```python
from scm.config.objects import Service
```

</div>

## Methods

### `create(data: Dict[str, Any]) -> ServiceResponseModel`

Creates a new service object.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the service object data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
service_data = {
    "name": "web-service",
    "protocol": {
        "tcp": {
            "port": "80,8080",
            "override": {
                "timeout": 30,
                "halfclose_timeout": 15,
            },
        }
    },
    "description": "HTTP service for web traffic",
    "folder": "Prisma Access",
}

new_service = service.create(service_data)
print(f"Created service with ID: {new_service.id}")
```

</div>

### `get(object_id: str) -> ServiceResponseModel`

Retrieves a service object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the service object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
service_id = "123e4567-e89b-12d3-a456-426655440000"
service_object = service.get(service_id)
print(f"Service Name: {service_object.name}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> ServiceResponseModel`

Updates an existing service object.

**Parameters:**

- `object_id` (str): The UUID of the service object.
- `data` (Dict[str, Any]): A dictionary containing the updated service data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Updated HTTP service description",
    "protocol": {
        "tcp": {
            "port": "80,8080,8000",
        }
    },
}

updated_service = service.update(service_id, update_data)
print(f"Updated service with ID: {updated_service.id}")
```

</div>

### `delete(object_id: str) -> None`

Deletes a service object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the service object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
service.delete(service_id)
print(f"Deleted service with ID: {service_id}")
```

</div>

###
`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, **filters) -> List[ServiceResponseModel]`

Lists service objects, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list services from.
- `snippet` (Optional[str]): The snippet to list services from.
- `device` (Optional[str]): The device to list services from.
- `**filters`: Additional filters (e.g., `names`, `tags`).

**Example:**

<div class="termy">

<!-- termynal -->

```python
services = service.list(folder='Prisma Access', names=['web-service', 'ssh-service'])

for svc in services:
    protocol = 'TCP' if svc.protocol.tcp else 'UDP'
    ports = svc.protocol.tcp.port if svc.protocol.tcp else svc.protocol.udp.port
    print(f"Service Name: {svc.name}, Protocol: {protocol}, Ports: {ports}")
```

</div>

---

## Usage Examples

### Example 1: Creating a TCP Service

<div class="termy">

<!-- termynal -->

```python
tcp_service_data = {
    "name": "web-service",
    "protocol": {
        "tcp": {
            "port": "80,443",
            "override": {
                "timeout": 60,
            },
        }
    },
    "description": "Web service for HTTP and HTTPS traffic",
    "folder": "Shared",
    "tag": ["web", "production"],
}

new_tcp_service = service.create(tcp_service_data)
print(f"Created TCP service with ID: {new_tcp_service.id}")
```

</div>

### Example 2: Creating a UDP Service

<div class="termy">

<!-- termynal -->

```python
udp_service_data = {
    "name": "dns-service",
    "protocol": {
        "udp": {
            "port": "53",
        }
    },
    "description": "DNS service",
    "snippet": "network-services",
}

new_udp_service = service.create(udp_service_data)
print(f"Created UDP service with ID: {new_udp_service.id}")
```

</div>

### Example 3: Updating a Service

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Updated web service description",
    "protocol": {
        "tcp": {
            "port": "80,443,8080",
            "override": {
                "timeout": 120,
                "halfclose_timeout": 30,
            },
        }
    },
    "tag": ["web", "production", "updated"],
}

updated_service = service.update(new_tcp_service.id, update_data)
print(f"Updated service: {updated_service.name}")
```

</div>

### Example 4: Listing Services with Filters

<div class="termy">

<!-- termynal -->

```python
filtered_services = service.list(
    folder='Shared',
    names=['web-service', 'dns-service'],
    tags=['production']
)

for svc in filtered_services:
    print(f"Service: {svc.name}, Tags: {svc.tag}")
```

</div>

### Example 5: Creating a Service in a Device Container

<div class="termy">

<!-- termynal -->

```python
device_service_data = {
    "name": "custom-app-service",
    "protocol": {
        "tcp": {
            "port": "9000-9100",
        }
    },
    "description": "Custom application service",
    "device": "firewall-01",
}

new_device_service = service.create(device_service_data)
print(f"Created device-specific service with ID: {new_device_service.id}")
```

</div>

### Example 6: Bulk Service Creation and Listing

<div class="termy">

<!-- termynal -->

```python
bulk_services = [
    {
        "name": f"app-service-{i}",
        "protocol": {"tcp": {"port": f"{8000 + i}"}},
        "folder": "Applications",
        "description": f"Application service {i}",
    }
    for i in range(1, 6)
]

created_services = [service.create(svc_data) for svc_data in bulk_services]

listed_services = service.list(folder='Applications')
for svc in listed_services:
    print(f"Listed service: {svc.name}, Port: {svc.protocol.tcp.port}")
```

</div>

---

## Full Example

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Service

# Initialize the SCM client
scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create a Service instance
service = Service(scm)

# Create a new service
service_data = {
    "name": "complex-web-service",
    "protocol": {
        "tcp": {
            "port": "80,443,8080-8090",
            "override": {
                "timeout": 300,
                "halfclose_timeout": 60,
                "timewait_timeout": 30,
            },
        }
    },
    "description": "Complex HTTP service with multiple ports",
    "folder": "Web Services",
    "tag": ["web", "complex", "high-availability"],
}

new_service = service.create(service_data)
print(f"Created service with ID: {new_service.id}")

# Get the created service
retrieved_service = service.get(new_service.id)
print(f"Retrieved service: {retrieved_service.name}")

# Update the service
update_data = {
    "description": "Updated complex HTTP service",
    "protocol": {
        "tcp": {
            "port": "80,443,8080-8095",
            "override": {
                "timeout": 360,
            },
        }
    },
    "tag": ["web", "complex", "high-availability", "updated"],
}

updated_service = service.update(new_service.id, update_data)
print(f"Updated service: {updated_service.name}")

# List services
services = service.list(folder='Web Services', tags=['complex'])
for svc in services:
    print(f"Service Name: {svc.name}, Ports: {svc.protocol.tcp.port}")

# Delete the service
service.delete(new_service.id)
print(f"Deleted service with ID: {new_service.id}")
```

</div>

---

## Related Models

- [ServiceRequestModel](../../models/objects/service_models.md#servicerequestmodel)
- [ServiceResponseModel](../../models/objects/service_models.md#serviceresponsemodel)

---
