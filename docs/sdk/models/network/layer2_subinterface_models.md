# Layer2 Subinterface Models

## Overview

The Layer2 Subinterface models provide structured validation for Layer 2 VLAN subinterface configuration. These subinterfaces operate at the data link layer for VLAN-tagged traffic.

### Models

- `Layer2SubinterfaceCreateModel`: For creating new subinterfaces
- `Layer2SubinterfaceUpdateModel`: For updating existing subinterfaces (includes `id`)
- `Layer2SubinterfaceResponseModel`: Response model from API operations

All models use `extra="forbid"` to reject undefined fields.

## Model Attributes

### Layer2SubinterfaceBaseModel

| Attribute  | Type   | Required | Default | Description                               |
|------------|--------|----------|---------|-------------------------------------------|
| `name`     | str    | Yes      | None    | Interface name (e.g., "ethernet1/1.100")  |
| `comment`  | str    | No       | None    | Description (max 1023 chars)              |
| `vlan_tag` | str    | Yes      | None    | VLAN tag (1-4096)                         |
| `folder`   | str    | No*      | None    | Folder container                          |
| `snippet`  | str    | No*      | None    | Snippet container                         |
| `device`   | str    | No*      | None    | Device container                          |

\* Exactly one container required for create operations

## VLAN Tag Validation

The `vlan_tag` field is validated with pattern: `^([1-9]\d{0,2}|[1-3]\d{3}|40[0-8]\d|409[0-6])$`

This ensures valid VLAN IDs from 1 to 4096.

## Usage Examples

### Create Subinterface

```python
from scm.models.network import Layer2SubinterfaceCreateModel

subinterface = Layer2SubinterfaceCreateModel(
    name="ethernet1/1.100",
    comment="Guest Network VLAN",
    vlan_tag="100",
    folder="Interfaces"
)
payload = subinterface.model_dump(exclude_unset=True)
```

### Using Dictionary

```python
data = {
    "name": "ethernet1/1.200",
    "vlan_tag": "200",
    "comment": "IoT VLAN",
    "folder": "Interfaces"
}
subinterface = Layer2SubinterfaceCreateModel(**data)
```
