# Layer2 Subinterface Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Layer2 Subinterface Model Attributes](#layer2-subinterface-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
7. [Managing Configuration Changes](#managing-configuration-changes)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Related Models](#related-models)

## Overview

The `Layer2Subinterface` class manages Layer 2 subinterface objects in Palo Alto Networks' Strata Cloud Manager. Layer 2 subinterfaces operate at the data link layer and are used for VLAN-tagged traffic on physical interfaces, enabling VLAN trunking.

## Core Methods

| Method     | Description                                                      | Parameters                                  | Return Type                           |
|------------|------------------------------------------------------------------|---------------------------------------------|---------------------------------------|
| `create()` | Creates a new Layer 2 subinterface                               | `data: Dict[str, Any]`                      | `Layer2SubinterfaceResponseModel`     |
| `get()`    | Retrieves a Layer 2 subinterface by ID                           | `object_id: str`                            | `Layer2SubinterfaceResponseModel`     |
| `update()` | Updates an existing Layer 2 subinterface                         | `subinterface: Layer2SubinterfaceUpdateModel` | `Layer2SubinterfaceResponseModel`   |
| `list()`   | Lists Layer 2 subinterfaces with optional filtering              | `folder`, `snippet`, `device`, plus filters | `List[Layer2SubinterfaceResponseModel]` |
| `fetch()`  | Fetches a single Layer 2 subinterface by name within a container | `name: str`, `folder`, `snippet`, `device`  | `Layer2SubinterfaceResponseModel`     |
| `delete()` | Deletes a Layer 2 subinterface by ID                             | `object_id: str`                            | `None`                                |

## Layer2 Subinterface Model Attributes

| Attribute  | Type   | Required | Default | Description                                      |
|------------|--------|----------|---------|--------------------------------------------------|
| `name`     | str    | Yes      | None    | Interface name (e.g., "ethernet1/1.100")         |
| `id`       | UUID   | Yes*     | None    | Unique identifier (*response/update only)        |
| `comment`  | str    | No       | None    | Description. Max 1023 chars                      |
| `vlan_tag` | str    | Yes      | None    | VLAN tag (1-4096)                                |
| `folder`   | str    | No**     | None    | Folder location. Max 64 chars                    |
| `snippet`  | str    | No**     | None    | Snippet location. Max 64 chars                   |
| `device`   | str    | No**     | None    | Device location. Max 64 chars                    |

\* Only required for update and response models
\** Exactly one container must be provided for create operations

## Exceptions

| Exception                    | HTTP Code | Description                            |
|------------------------------|-----------|----------------------------------------|
| `InvalidObjectError`         | 400       | Invalid data or parameters             |
| `MissingQueryParameterError` | 400       | Missing required parameters            |
| `ObjectNotPresentError`      | 404       | Interface not found                    |
| `AuthenticationError`        | 401       | Authentication failed                  |
| `ServerError`                | 500       | Internal server error                  |

## Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

layer2_subinterfaces = client.layer2_subinterface
```

## Usage Examples

### Creating Layer2 Subinterfaces

```python
# Create Layer 2 subinterface with VLAN tag
subinterface_data = {
    "name": "ethernet1/1.100",
    "comment": "VLAN 100 - Guest Network",
    "vlan_tag": "100",
    "folder": "Interfaces"
}

result = client.layer2_subinterface.create(subinterface_data)
print(f"Created subinterface: {result.id}")

# Create multiple subinterfaces for different VLANs
vlans = [
    {"name": "ethernet1/1.200", "vlan_tag": "200", "comment": "VLAN 200 - IoT"},
    {"name": "ethernet1/1.300", "vlan_tag": "300", "comment": "VLAN 300 - Voice"},
]

for vlan in vlans:
    vlan["folder"] = "Interfaces"
    result = client.layer2_subinterface.create(vlan)
    print(f"Created: {result.name}")
```

### Retrieving Layer2 Subinterfaces

```python
# Fetch by name
subinterface = client.layer2_subinterface.fetch(
    name="ethernet1/1.100",
    folder="Interfaces"
)
print(f"Found: {subinterface.name}, VLAN: {subinterface.vlan_tag}")

# Get by ID
subinterface_by_id = client.layer2_subinterface.get(subinterface.id)
```

### Updating Layer2 Subinterfaces

```python
existing = client.layer2_subinterface.fetch(
    name="ethernet1/1.100",
    folder="Interfaces"
)

existing.comment = "Updated Guest Network VLAN"

updated = client.layer2_subinterface.update(existing)
```

### Listing Layer2 Subinterfaces

```python
# List all Layer 2 subinterfaces
subinterfaces = client.layer2_subinterface.list(folder="Interfaces")

for sub in subinterfaces:
    print(f"Name: {sub.name}, VLAN: {sub.vlan_tag}")

# Filter by VLAN tag
vlan100 = client.layer2_subinterface.list(folder="Interfaces", vlan_tag="100")
```

### Deleting Layer2 Subinterfaces

```python
client.layer2_subinterface.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Managing Configuration Changes

```python
result = client.commit(
    folders=["Interfaces"],
    description="Updated Layer 2 subinterfaces",
    sync=True
)
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError

try:
    subinterface = client.layer2_subinterface.create({
        "name": "ethernet1/1.100",
        "vlan_tag": "5000",  # Error: VLAN out of range
        "folder": "Interfaces"
    })
except InvalidObjectError as e:
    print(f"Invalid configuration: {e.message}")
```

## Best Practices

1. **Naming Convention** - Use format `parent_interface.vlan_tag` (e.g., "ethernet1/1.100")
2. **VLAN Planning** - Plan VLAN assignments before creating subinterfaces
3. **Documentation** - Use comments to describe VLAN purpose
4. **Parent Interface** - Ensure parent interface is configured for trunking

## Related Models

- [Layer2SubinterfaceCreateModel](../../models/network/layer2_subinterface_models.md)
- [Layer2SubinterfaceUpdateModel](../../models/network/layer2_subinterface_models.md)
- [Layer2SubinterfaceResponseModel](../../models/network/layer2_subinterface_models.md)
