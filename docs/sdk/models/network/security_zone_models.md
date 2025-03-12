# Security Zone Models

## Overview

The Security Zone models provide a structured way to represent and validate security zone configuration data for Palo Alto Networks' Strata Cloud Manager. These models ensure data integrity when creating and updating security zones, enforcing proper network interface types, container specifications, and field validations.

## Attributes

### SecurityZoneBaseModel

This is the base model containing fields common to all security zone operations.

| Attribute                    | Type                 | Required      | Default        | Description                                                                                                     |
|------------------------------|----------------------|---------------|----------------|-----------------------------------------------------------------------------------------------------------------|
| name                         | str                  | Yes           | –              | The name of the security zone. Must match pattern `^[0-9a-zA-Z._-]+$` and be ≤ 63 chars.                        |
| enable_user_identification   | bool                 | No            | None           | Enable user identification for this zone.                                                                       |
| enable_device_identification | bool                 | No            | None           | Enable device identification for this zone.                                                                     |
| dos_profile                  | str                  | No            | None           | DoS profile name associated with this zone.                                                                     |
| dos_log_setting              | str                  | No            | None           | DoS log setting name for this zone.                                                                            |
| network                      | NetworkConfig        | No            | None           | Network configuration with interface assignments.                                                               |
| user_acl                     | UserAcl              | No            | None           | User access control list configuration.                                                                         |
| device_acl                   | DeviceAcl            | No            | None           | Device access control list configuration.                                                                       |
| folder                       | str                  | Conditionally | None           | The folder in which the resource is defined. Must match pattern `^[a-zA-Z\d\-_. ]+$` and be ≤ 64 chars.         |
| snippet                      | str                  | Conditionally | None           | The snippet in which the resource is defined. Must match pattern `^[a-zA-Z\d\-_. ]+$` and be ≤ 64 chars.        |
| device                       | str                  | Conditionally | None           | The device in which the resource is defined. Must match pattern `^[a-zA-Z\d\-_. ]+$` and be ≤ 64 chars.         |

### NetworkConfig

This model defines the network configuration for a security zone, including interfaces and security settings.

| Attribute                       | Type                 | Required      | Default        | Description                                                                                                     |
|--------------------------------|----------------------|---------------|----------------|-----------------------------------------------------------------------------------------------------------------|
| zone_protection_profile        | str                  | No            | None           | Zone protection profile name for enhanced security.                                                             |
| enable_packet_buffer_protection| bool                 | No            | None           | Enable packet buffer protection for this zone.                                                                  |
| log_setting                    | str                  | No            | None           | Log setting name for this zone.                                                                                 |
| tap                            | List[str]            | No*           | None           | TAP interfaces assigned to this zone.                                                                           |
| virtual_wire                   | List[str]            | No*           | None           | Virtual wire interfaces assigned to this zone.                                                                  |
| layer2                         | List[str]            | No*           | None           | Layer 2 interfaces assigned to this zone.                                                                       |
| layer3                         | List[str]            | No*           | None           | Layer 3 interfaces assigned to this zone.                                                                       |
| tunnel                         | Dict[str, Any]       | No*           | None           | Tunnel configuration for this zone.                                                                             |
| external                       | List[str]            | No*           | None           | External interfaces assigned to this zone.                                                                      |

*\* Only one network interface type (tap, virtual_wire, layer2, layer3, tunnel, or external) can be configured at a time.*

### UserAcl

This model defines the user access control list configuration.

| Attribute     | Type                | Required | Default        | Description                          |
|---------------|---------------------|----------|----------------|--------------------------------------|
| include_list  | List[str]           | No       | Empty list     | List of users to include             |
| exclude_list  | List[str]           | No       | Empty list     | List of users to exclude             |

### DeviceAcl

This model defines the device access control list configuration.

| Attribute     | Type                | Required | Default        | Description                          |
|---------------|---------------------|----------|----------------|--------------------------------------|
| include_list  | List[str]           | No       | Empty list     | List of devices to include           |
| exclude_list  | List[str]           | No       | Empty list     | List of devices to exclude           |

### SecurityZoneCreateModel

Inherits all fields from `SecurityZoneBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### SecurityZoneUpdateModel

Extends `SecurityZoneBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                                |
|-----------|------|----------|---------|------------------------------------------------------------|
| id        | UUID | Yes      | –       | The unique identifier of the security zone.               |

### SecurityZoneResponseModel

Extends `SecurityZoneBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                                |
|-----------|------|----------|---------|------------------------------------------------------------|
| id        | UUID | Yes      | –       | The unique identifier of the security zone.               |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a security zone (`SecurityZoneCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When the network configuration specifies more than one network interface type (e.g., both `layer3` and `layer2` are set).
- When the security zone name does not match the required pattern or exceeds the maximum length.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Field Validators in `NetworkConfig`

- **validate_network_type**:
  Ensures that only one network interface type is configured at a time. If multiple interface types are set, it raises a `ValueError`.

### Container Validation in `SecurityZoneCreateModel`

- **validate_container**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a Security Zone

#### Using a Dictionary with Layer 3 Interfaces

<div class="termy">

<!-- termynal -->
```python
from scm.models.network import SecurityZoneCreateModel

zone_data = {
    "name": "trust-zone",
    "enable_user_identification": True,
    "enable_device_identification": False,
    "network": {
        "layer3": ["ethernet1/1", "ethernet1/2"],
        "zone_protection_profile": "default",
        "enable_packet_buffer_protection": True
    },
    "user_acl": {
        "include_list": ["user1", "user2"],
        "exclude_list": []
    },
    "folder": "Security Zones"
}

# Validate and create model instance
security_zone = SecurityZoneCreateModel(**zone_data)
payload = security_zone.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

</div>

#### Using the Model Directly with Virtual Wire Interfaces

<div class="termy">

<!-- termynal -->
```python
from scm.models.network import SecurityZoneCreateModel, NetworkConfig, UserAcl, DeviceAcl

# Create the network configuration
network_config = NetworkConfig(
    virtual_wire=["ethernet1/3", "ethernet1/4"],
    zone_protection_profile="default"
)

# Create user ACL
user_acl = UserAcl(
    include_list=["admin", "operator"],
    exclude_list=["guest"]
)

# Create security zone
security_zone = SecurityZoneCreateModel(
    name="virtual-wire-zone",
    enable_user_identification=True,
    enable_device_identification=True,
    network=network_config,
    user_acl=user_acl,
    folder="Security Zones"
)
payload = security_zone.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

</div>

### Updating a Security Zone

<div class="termy">

<!-- termynal -->
```python
import uuid
from scm.models.network import SecurityZoneUpdateModel, NetworkConfig

# Create network configuration for update
network_config = NetworkConfig(
    layer3=["ethernet1/1", "ethernet1/2", "ethernet1/3"],  # Added a new interface
    zone_protection_profile="enhanced-security",
    enable_packet_buffer_protection=True
)

# Update data
update_data = {
    "id": str(uuid.uuid4()),
    "name": "trust-zone",
    "enable_device_identification": True,  # Change this setting
    "network": network_config,
    "folder": "Security Zones"
}

updated_zone = SecurityZoneUpdateModel(**update_data)
payload = updated_zone.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

</div>

### Creating a Security Zone with ACLs

<div class="termy">

<!-- termynal -->
```python
from scm.models.network import SecurityZoneCreateModel, UserAcl, DeviceAcl

# Create a security zone with both user and device ACLs
zone_data = {
    "name": "restricted-zone",
    "enable_user_identification": True,
    "enable_device_identification": True,
    "network": {
        "layer3": ["ethernet1/5"]
    },
    "user_acl": {
        "include_list": ["admin", "security-team"],
        "exclude_list": ["contractor", "guest"]
    },
    "device_acl": {
        "include_list": ["corporate-laptops"],
        "exclude_list": ["byod-devices", "unmanaged-devices"]
    },
    "folder": "Security Zones"
}

security_zone = SecurityZoneCreateModel(**zone_data)
payload = security_zone.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

</div>

## Related Models and Enums

- **Enums:**
  - `NetworkInterfaceType`: Allowed values are `TAP`, `VIRTUAL_WIRE`, `LAYER2`, `LAYER3`, `TUNNEL`, `EXTERNAL`.

- **Models:**
  - `NetworkConfig`: Model for network interface and security configuration.
  - `UserAcl`: Model for user access control list configuration.
  - `DeviceAcl`: Model for device access control list configuration.
  - `SecurityZoneBaseModel`: Base model for security zone operations.
  - `SecurityZoneCreateModel`: Model for creating security zones.
  - `SecurityZoneUpdateModel`: Model for updating security zones.
  - `SecurityZoneResponseModel`: Model for security zone responses.
