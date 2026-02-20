# Route Access List Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Route Access List models provide a structured way to represent and validate route access list configuration data for Palo Alto Networks' Strata Cloud Manager. Route access lists are used to filter routes based on source and destination IP addresses with optional wildcard masks, commonly applied in BGP and OSPF routing policies.

### Models

The module provides the following Pydantic models:

- `RouteAccessListBaseModel`: Base model with fields common to all route access list operations
- `RouteAccessListCreateModel`: Model for creating new route access lists
- `RouteAccessListUpdateModel`: Model for updating existing route access lists
- `RouteAccessListResponseModel`: Response model for route access list operations
- `RouteAccessListType`: Access list type container
- `RouteAccessListIpv4`: IPv4 access list container
- `RouteAccessListIpv4Entry`: Individual IPv4 access list entry
- `RouteAccessListSourceAddress`: Source address with optional wildcard mask
- `RouteAccessListDestinationAddress`: Destination address with optional wildcard mask

The `RouteAccessListBaseModel` and `RouteAccessListCreateModel` / `RouteAccessListUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `RouteAccessListResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### RouteAccessListBaseModel

This is the base model containing fields common to all route access list operations.

| Attribute   | Type                 | Required | Default | Description                                                     |
|-------------|----------------------|----------|---------|-----------------------------------------------------------------|
| name        | str                  | Yes      | None    | Route access list name.                                         |
| description | str                  | No       | None    | Description.                                                    |
| type        | RouteAccessListType  | No       | None    | Access list type configuration.                                 |
| folder      | str                  | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet     | str                  | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device      | str                  | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### RouteAccessListCreateModel

Inherits all fields from `RouteAccessListBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### RouteAccessListUpdateModel

Extends `RouteAccessListBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                     |
|-----------|------|----------|---------|-------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the route access list  |

### RouteAccessListResponseModel

Extends `RouteAccessListBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                     |
|-----------|------|----------|---------|-------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the route access list  |

> **Note:** The `RouteAccessListResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Supporting Models

### RouteAccessListType

Container for the access list type.

| Attribute | Type                | Required | Default | Description          |
|-----------|---------------------|----------|---------|----------------------|
| ipv4      | RouteAccessListIpv4 | No       | None    | IPv4 access list.    |

### RouteAccessListIpv4

IPv4 access list container holding the list of entries.

| Attribute  | Type                          | Required | Default | Description               |
|------------|-------------------------------|----------|---------|---------------------------|
| ipv4_entry | List[RouteAccessListIpv4Entry] | No       | None    | IPv4 access list entries. |

### RouteAccessListIpv4Entry

Individual IPv4 access list entry with sequence number, action, and address matching.

| Attribute           | Type                              | Required | Default | Description                                     |
|---------------------|-----------------------------------|----------|---------|-------------------------------------------------|
| name                | int                               | No       | None    | Sequence number (1-65535).                       |
| action              | str                               | No       | None    | Action: `deny` or `permit`. Pattern: `^(deny\|permit)$` |
| source_address      | RouteAccessListSourceAddress      | No       | None    | Source address configuration.                    |
| destination_address | RouteAccessListDestinationAddress | No       | None    | Destination address configuration.               |

### RouteAccessListSourceAddress

Source address configuration with optional wildcard mask.

| Attribute | Type | Required | Default | Description              |
|-----------|------|----------|---------|--------------------------|
| address   | str  | No       | None    | Source IP address.        |
| wildcard  | str  | No       | None    | Source IP wildcard mask.  |

### RouteAccessListDestinationAddress

Destination address configuration with optional wildcard mask.

| Attribute | Type | Required | Default | Description                   |
|-----------|------|----------|---------|-------------------------------|
| address   | str  | No       | None    | Destination IP address.        |
| wildcard  | str  | No       | None    | Destination IP wildcard mask.  |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a route access list (`RouteAccessListCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When an entry sequence number is outside the valid range (1-65535).
- When an entry action is not `deny` or `permit`.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Container Validation in `RouteAccessListCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a Route Access List

#### Using a Dictionary

```python
from scm.models.network import RouteAccessListCreateModel

acl_data = {
    "name": "acl-1",
    "description": "Block private networks",
    "type": {
        "ipv4": {
            "ipv4_entry": [
                {
                    "name": 10,
                    "action": "deny",
                    "source_address": {
                        "address": "10.0.0.0",
                        "wildcard": "0.255.255.255",
                    },
                },
                {
                    "name": 20,
                    "action": "deny",
                    "source_address": {
                        "address": "172.16.0.0",
                        "wildcard": "0.15.255.255",
                    },
                },
                {
                    "name": 30,
                    "action": "permit",
                    "source_address": {
                        "address": "0.0.0.0",
                        "wildcard": "255.255.255.255",
                    },
                },
            ],
        },
    },
    "folder": "Routing",
}

# Validate and create model instance
acl = RouteAccessListCreateModel(**acl_data)
payload = acl.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import (
    RouteAccessListCreateModel,
    RouteAccessListType,
    RouteAccessListIpv4,
    RouteAccessListIpv4Entry,
    RouteAccessListSourceAddress,
)

# Build access list entries
entries = [
    RouteAccessListIpv4Entry(
        name=10,
        action="deny",
        source_address=RouteAccessListSourceAddress(
            address="10.0.0.0",
            wildcard="0.255.255.255",
        ),
    ),
    RouteAccessListIpv4Entry(
        name=20,
        action="permit",
        source_address=RouteAccessListSourceAddress(
            address="0.0.0.0",
            wildcard="255.255.255.255",
        ),
    ),
]

# Create the access list
acl = RouteAccessListCreateModel(
    name="acl-2",
    description="Filter specific networks",
    type=RouteAccessListType(
        ipv4=RouteAccessListIpv4(ipv4_entry=entries),
    ),
    folder="Routing",
)
payload = acl.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a Route Access List

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing access list
existing = client.route_access_list.fetch(name="acl-1", folder="Routing")

# Modify description
existing.description = "Updated filter for private networks"

# Pass modified object to update()
updated = client.route_access_list.update(existing)
print(f"Updated access list: {updated.name}")
```
