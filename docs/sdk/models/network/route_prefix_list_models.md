# Route Prefix List Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Route Prefix List models provide a structured way to represent and validate route prefix list configuration data for Palo Alto Networks' Strata Cloud Manager. Route prefix lists are used for prefix-based route filtering in BGP and OSPF routing policies. Each entry can match a specific network with optional greater-than-or-equal (ge) and less-than-or-equal (le) prefix length modifiers, or match any network using the special `any` keyword.

### Models

The module provides the following Pydantic models:

- `RoutePrefixListBaseModel`: Base model with fields common to all route prefix list operations
- `RoutePrefixListCreateModel`: Model for creating new route prefix lists
- `RoutePrefixListUpdateModel`: Model for updating existing route prefix lists
- `RoutePrefixListResponseModel`: Response model for route prefix list operations
- `RoutePrefixListIpv4`: IPv4 prefix list container
- `RoutePrefixListIpv4Entry`: Individual IPv4 prefix list entry
- `RoutePrefixListPrefix`: Prefix configuration (oneOf: `network` "any" or `entry`)
- `RoutePrefixListPrefixEntry`: Prefix entry with network and optional ge/le

The `RoutePrefixListBaseModel` and `RoutePrefixListCreateModel` / `RoutePrefixListUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `RoutePrefixListResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### RoutePrefixListBaseModel

This is the base model containing fields common to all route prefix list operations.

| Attribute   | Type                 | Required | Default | Description                                                     |
|-------------|----------------------|----------|---------|-----------------------------------------------------------------|
| name        | str                  | Yes      | None    | Filter prefix list name.                                        |
| description | str                  | No       | None    | Description.                                                    |
| ipv4        | RoutePrefixListIpv4  | No       | None    | IPv4 prefix list configuration.                                 |
| folder      | str                  | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet     | str                  | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device      | str                  | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### RoutePrefixListCreateModel

Inherits all fields from `RoutePrefixListBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### RoutePrefixListUpdateModel

Extends `RoutePrefixListBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                    |
|-----------|------|----------|---------|------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the route prefix list |

### RoutePrefixListResponseModel

Extends `RoutePrefixListBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                    |
|-----------|------|----------|---------|------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the route prefix list |

> **Note:** The `RoutePrefixListResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Supporting Models

### RoutePrefixListIpv4

IPv4 prefix list container holding the list of entries.

| Attribute  | Type                           | Required | Default | Description              |
|------------|--------------------------------|----------|---------|--------------------------|
| ipv4_entry | List[RoutePrefixListIpv4Entry] | No       | None    | IPv4 prefix list entries.|

### RoutePrefixListIpv4Entry

Individual IPv4 prefix list entry with sequence number, action, and prefix matching.

| Attribute | Type                  | Required | Default | Description                                           |
|-----------|-----------------------|----------|---------|-------------------------------------------------------|
| name      | int                   | No       | None    | Sequence number (1-65535).                             |
| action    | str                   | No       | None    | Action: `deny` or `permit`. Pattern: `^(deny\|permit)$` |
| prefix    | RoutePrefixListPrefix | No       | None    | Prefix configuration.                                 |

### RoutePrefixListPrefix

Prefix configuration. Uses oneOf semantics: `network` and `entry` are mutually exclusive.

| Attribute | Type                       | Required | Default | Description                                              |
|-----------|----------------------------|----------|---------|----------------------------------------------------------|
| network   | str                        | No*      | None    | Network keyword (must be `any`). Pattern: `^any$`        |
| entry     | RoutePrefixListPrefixEntry | No*      | None    | Prefix entry with network address and optional ge/le.    |

\* `network` and `entry` are mutually exclusive.

### RoutePrefixListPrefixEntry

Prefix entry with network address and optional ge/le modifiers.

| Attribute              | Type | Required | Default | Description                                    |
|------------------------|------|----------|---------|------------------------------------------------|
| network                | str  | No       | None    | Network address (e.g., "10.0.0.0/8").          |
| greater_than_or_equal  | int  | No       | None    | Greater than or equal to prefix length (0-32). |
| less_than_or_equal     | int  | No       | None    | Less than or equal to prefix length (0-32).    |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a route prefix list (`RoutePrefixListCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When both `network` and `entry` are set in `RoutePrefixListPrefix` (mutually exclusive).
- When an entry sequence number is outside the valid range (1-65535).
- When an entry action is not `deny` or `permit`.
- When ge/le values are outside the valid range (0-32).
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### OneOf Validator in `RoutePrefixListPrefix`

- **validate_prefix_type**:
  Ensures that `network` and `entry` are mutually exclusive. If both are set, it raises a `ValueError`. A prefix can either match any network (using `network: "any"`) or a specific prefix entry, but not both.

### Container Validation in `RoutePrefixListCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a Route Prefix List

#### Using a Dictionary

```python
from scm.models.network import RoutePrefixListCreateModel

prefix_list_data = {
    "name": "prefix-list-1",
    "description": "Allow default and specific prefixes",
    "ipv4": {
        "ipv4_entry": [
            {
                "name": 10,
                "action": "permit",
                "prefix": {
                    "entry": {
                        "network": "10.0.0.0/8",
                        "greater_than_or_equal": 16,
                        "less_than_or_equal": 24,
                    },
                },
            },
            {
                "name": 20,
                "action": "permit",
                "prefix": {
                    "entry": {
                        "network": "172.16.0.0/12",
                        "greater_than_or_equal": 16,
                        "less_than_or_equal": 28,
                    },
                },
            },
            {
                "name": 100,
                "action": "deny",
                "prefix": {
                    "network": "any",
                },
            },
        ],
    },
    "folder": "Routing",
}

# Validate and create model instance
prefix_list = RoutePrefixListCreateModel(**prefix_list_data)
payload = prefix_list.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import (
    RoutePrefixListCreateModel,
    RoutePrefixListIpv4,
    RoutePrefixListIpv4Entry,
    RoutePrefixListPrefix,
    RoutePrefixListPrefixEntry,
)

# Build prefix list entries
entries = [
    RoutePrefixListIpv4Entry(
        name=10,
        action="permit",
        prefix=RoutePrefixListPrefix(
            entry=RoutePrefixListPrefixEntry(
                network="10.0.0.0/8",
                greater_than_or_equal=16,
                less_than_or_equal=24,
            ),
        ),
    ),
    RoutePrefixListIpv4Entry(
        name=100,
        action="deny",
        prefix=RoutePrefixListPrefix(network="any"),
    ),
]

# Create the prefix list
prefix_list = RoutePrefixListCreateModel(
    name="prefix-list-2",
    description="Specific prefix filtering",
    ipv4=RoutePrefixListIpv4(ipv4_entry=entries),
    folder="Routing",
)
payload = prefix_list.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a Route Prefix List

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing prefix list
existing = client.route_prefix_list.fetch(name="prefix-list-1", folder="Routing")

# Modify description
existing.description = "Updated prefix filtering rules"

# Pass modified object to update()
updated = client.route_prefix_list.update(existing)
print(f"Updated prefix list: {updated.name}")
```
