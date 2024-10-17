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

## Usage Example

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
    "name": "web-service",
    "protocol": {
        "tcp": {
            "port": "80,8080",
        }
    },
    "description": "HTTP service",
    "folder": "Prisma Access",
}

new_service = service.create(service_data)
print(f"Created service with ID: {new_service.id}")

# List services
services = service.list(folder='Prisma Access')
for svc in services:
    protocol = 'TCP' if svc.protocol.tcp else 'UDP'
    ports = svc.protocol.tcp.port if svc.protocol.tcp else svc.protocol.udp.port
    print(f"Service Name: {svc.name}, Protocol: {protocol}, Ports: {ports}")
```

</div>


---

## Related Models

- [ServiceRequestModel](../../models/objects/service_models.md#servicerequestmodel)
- [ServiceResponseModel](../../models/objects/service_models.md#serviceresponsemodel)

---
