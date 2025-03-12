# Security Zones Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Security Zone Model Attributes](#security-zone-model-attributes)
4. [Network Interface Types](#network-interface-types)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
   1. [Creating Security Zones](#creating-security-zones)
   2. [Retrieving Security Zones](#retrieving-security-zones)
   3. [Updating Security Zones](#updating-security-zones)
   4. [Listing Security Zones](#listing-security-zones)
   5. [Deleting Security Zones](#deleting-security-zones)
8. [Managing Configuration Changes](#managing-configuration-changes)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Full Script Examples](#full-script-examples)
12. [Related Models](#related-models)

## Overview

The `SecurityZone` class manages security zone objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete security zones. Additionally, it provides client-side filtering for listing operations and enforces container requirements using the `folder`, `snippet`, or `device` parameters.

## Core Methods

| Method     | Description                                                  | Parameters                                                                                                                                                | Return Type                      |
|------------|--------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|
| `create()` | Creates a new security zone object                           | `data: Dict[str, Any]`                                                                                                                                     | `SecurityZoneResponseModel`       |
| `get()`    | Retrieves a security zone object by its unique ID            | `object_id: str`                                                                                                                                          | `SecurityZoneResponseModel`       |
| `update()` | Updates an existing security zone object                     | `zone: SecurityZoneUpdateModel`                                                                                                                           | `SecurityZoneResponseModel`       |
| `list()`   | Lists security zone objects with optional filtering          | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters                          | `List[SecurityZoneResponseModel]` |
| `fetch()`  | Fetches a single security zone by its name within a container| `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                                                    | `SecurityZoneResponseModel`       |
| `delete()` | Deletes a security zone object by its ID                     | `object_id: str`                                                                                                                                          | `None`                           |

## Security Zone Model Attributes

| Attribute                   | Type                 | Required      | Description                                                |
|-----------------------------|--------------------- |---------------|------------------------------------------------------------|
| `name`                      | str                  | Yes           | The name of the security zone                              |
| `id`                        | UUID                 | Yes*          | Unique identifier (response only)                          |
| `enable_user_identification`| bool                 | No            | Enables user identification                                |
| `enable_device_identification`| bool               | No            | Enables device identification                              |
| `dos_profile`               | str                  | No            | Denial of Service profile name                             |
| `dos_log_setting`           | str                  | No            | DoS log setting name                                       |
| `network`                   | NetworkConfig        | No            | Network configuration for the zone                         |
| `user_acl`                  | UserAcl              | No            | User access control list configuration                     |
| `device_acl`                | DeviceAcl            | No            | Device access control list configuration                   |
| `folder`                    | str                  | Conditionally | The folder container where the security zone is defined    |
| `snippet`                   | str                  | Conditionally | The snippet container (if applicable)                      |
| `device`                    | str                  | Conditionally | The device container (if applicable)                       |

*\* The `id` field is assigned by the system and is only present in response objects.*

## Network Interface Types

Security zones can use different network interface types, following a mutual exclusion pattern where exactly one type must be provided:

### 1. Layer 3 Interfaces

Layer 3 interfaces are the most common type and define routed interfaces.

<div class="termy">

<!-- termynal -->
```python
security_zone_data = {
   "name": "trust-zone",
   "network": {
      "layer3": ["ethernet1/1", "ethernet1/2"],
      "zone_protection_profile": "default",
      "enable_packet_buffer_protection": True
   },
   "folder": "Security Zones"
}
```

</div>

### 2. Layer 2 Interfaces

Layer 2 interfaces operate at the data link layer.

<div class="termy">

<!-- termynal -->
```python
security_zone_data = {
   "name": "layer2-zone",
   "network": {
      "layer2": ["ethernet1/3", "ethernet1/4"],
      "log_setting": "default-log-setting"
   },
   "folder": "Security Zones"
}
```

</div>

### 3. Virtual Wire Interfaces

Virtual wire interfaces connect two interfaces together.

<div class="termy">

<!-- termynal -->
```python
security_zone_data = {
   "name": "virtual-wire-zone",
   "network": {
      "virtual_wire": ["ethernet1/5", "ethernet1/6"]
   },
   "folder": "Security Zones"
}
```

</div>

### 4. Tunnel Interfaces

Tunnel interfaces are used for VPN and other tunneling technologies.

<div class="termy">

<!-- termynal -->
```python
security_zone_data = {
   "name": "tunnel-zone",
   "network": {
      "tunnel": {}  # Configuration depends on the tunnel type
   },
   "folder": "Security Zones"
}
```

</div>

### 5. TAP Interfaces

TAP interfaces are used for traffic monitoring without affecting the traffic flow.

<div class="termy">

<!-- termynal -->
```python
security_zone_data = {
   "name": "tap-zone",
   "network": {
      "tap": ["ethernet1/7"]
   },
   "folder": "Security Zones"
}
```

</div>

### 6. External Interfaces

External interfaces are used for connecting to external networks.

<div class="termy">

<!-- termynal -->
```python
security_zone_data = {
   "name": "external-zone",
   "network": {
      "external": ["ethernet1/8"]
   },
   "folder": "Security Zones"
}
```

</div>

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |

In addition to these HTTP exceptions, the model validation may raise `ValueError` for various validation issues, such as:

- Using invalid container combinations (more than one of `folder`, `snippet`, or `device`)
- Configuring more than one network interface type for a security zone
- Using invalid patterns for security zone names
- Invalid field types or values

## Basic Configuration

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize client using the unified client approach
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id",
   security_zone_max_limit=2500  # Optional: set custom max_limit for security zones
)

# Access the security_zone module directly through the client
# client.security_zone is automatically initialized for you
```

</div>

You can also use the traditional approach if preferred:

<div class="termy">

<!-- termynal -->
```python
from scm.client import Scm
from scm.config.network import SecurityZone

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize SecurityZone object with a custom max_limit (optional)
security_zone = SecurityZone(client, max_limit=2500)
```

</div>

## Usage Examples

### Creating Security Zones

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Define security zone configuration with Layer 3 interfaces
security_zone_data = {
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

# Create a new security zone
new_security_zone = client.security_zone.create(security_zone_data)
print(f"Created security zone with ID: {new_security_zone.id}")

# Create a security zone with Layer 2 interfaces
layer2_zone_data = {
   "name": "layer2-zone",
   "enable_user_identification": False,
   "network": {
      "layer2": ["ethernet1/3", "ethernet1/4"],
      "log_setting": "default-log-setting"
   },
   "folder": "Security Zones"
}

layer2_zone = client.security_zone.create(layer2_zone_data)
print(f"Created Layer 2 security zone with ID: {layer2_zone.id}")
```

</div>

### Retrieving Security Zones

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Retrieve a security zone by name using fetch()
fetched_zone = client.security_zone.fetch(
   name="trust-zone",
   folder="Security Zones"
)
print(f"Fetched Security Zone: {fetched_zone.name}")

# Retrieve a security zone by its unique ID using get()
zone_by_id = client.security_zone.get(fetched_zone.id)
print(f"Security Zone ID: {zone_by_id.id}, Name: {zone_by_id.name}")
```

</div>

### Updating Security Zones

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient
from scm.models.network import SecurityZoneUpdateModel, NetworkConfig

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Assume we have fetched the existing security zone
existing_zone = client.security_zone.fetch(
   name="trust-zone",
   folder="Security Zones"
)

# Create a new network configuration
network_config = NetworkConfig(
   layer3=["ethernet1/1", "ethernet1/2", "ethernet1/3"],  # Added a new interface
   zone_protection_profile="enhanced-security",  # Changed protection profile
   enable_packet_buffer_protection=True
)

# Update with new configuration
updated_data = {
   "id": existing_zone.id,
   "name": existing_zone.name,  # Name must be included in updates
   "enable_device_identification": True,  # Change this setting
   "network": network_config,
   "folder": "Security Zones"
}
zone_update = SecurityZoneUpdateModel(**updated_data)

# Update the security zone
updated_zone = client.security_zone.update(zone_update)
print(f"Updated Security Zone with new interface configuration")
```

</div>

### Listing Security Zones

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# List security zones in the "Security Zones" folder with additional filtering
zones_list = client.security_zone.list(
   folder="Security Zones",
   enable_user_identification=True  # Filter by user identification status
)

# Iterate and process each security zone
for zone in zones_list:
   print(f"Name: {zone.name}")

   # Check network configuration
   if zone.network:
      if zone.network.layer3:
         print(f"  Type: Layer 3, Interfaces: {', '.join(zone.network.layer3)}")
      elif zone.network.layer2:
         print(f"  Type: Layer 2, Interfaces: {', '.join(zone.network.layer2)}")
      elif zone.network.virtual_wire:
         print(f"  Type: Virtual Wire, Interfaces: {', '.join(zone.network.virtual_wire)}")
      elif zone.network.tunnel:
         print("  Type: Tunnel")
      elif zone.network.tap:
         print(f"  Type: TAP, Interfaces: {', '.join(zone.network.tap)}")
      elif zone.network.external:
         print(f"  Type: External, Interfaces: {', '.join(zone.network.external)}")

   # Display user identification status
   print(f"  User Identification Enabled: {zone.enable_user_identification}")
   print(f"  Device Identification Enabled: {zone.enable_device_identification}")
```

</div>

### Deleting Security Zones

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Delete a security zone by its unique ID
zone_id_to_delete = "123e4567-e89b-12d3-a456-426655440000"
client.security_zone.delete(zone_id_to_delete)
print(f"Security Zone {zone_id_to_delete} deleted successfully.")
```

</div>

## Managing Configuration Changes

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a security zone
security_zone_data = {
   "name": "dmz-zone",
   "enable_user_identification": False,
   "enable_device_identification": False,
   "network": {
      "layer3": ["ethernet1/7", "ethernet1/8"],
      "zone_protection_profile": "strict",
   },
   "folder": "Security Zones"
}

# Create the security zone
new_zone = client.security_zone.create(security_zone_data)
print(f"Created security zone with ID: {new_zone.id}")

# Commit the configuration changes
commit_result = client.operations.commit(
   description="Added DMZ security zone",
   folders=["Security Zones"]
)

# Get the job ID from the commit operation
job_id = commit_result.id
print(f"Commit job initiated with ID: {job_id}")

# Monitor the job status
job_result = client.operations.get_job_status(job_id)
print(f"Job status: {job_result.status}")

# Wait for job completion
import time
while job_result.status not in ["FIN", "FAIL"]:
   time.sleep(5)
   job_result = client.operations.get_job_status(job_id)
   print(f"Current job status: {job_result.status}")

if job_result.status == "FIN":
   print("Security zone changes committed successfully")
else:
   print(f"Commit failed: {job_result.details}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient
from scm.exceptions import (
   InvalidObjectError,
   MissingQueryParameterError,
   ApiError
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Attempt to create a security zone with multiple network types
   invalid_zone = {
      "name": "invalid-zone",
      "network": {
         "layer3": ["ethernet1/1"],
         "layer2": ["ethernet1/2"]  # Multiple types are not allowed
      },
      "folder": "Security Zones"
   }
   result = client.security_zone.create(invalid_zone)

except InvalidObjectError as e:
   print(f"Invalid object error: {e.message}")
   print(f"HTTP status: {e.http_status_code}")
   print(f"Details: {e.details}")

try:
   # Attempt to fetch a security zone without specifying a container
   zone = client.security_zone.fetch(name="some-zone")

except MissingQueryParameterError as e:
   print(f"Missing parameter error: {e.message}")

try:
   # General API error handling
   zone_id = "non-existent-id"
   client.security_zone.get(zone_id)

except ApiError as e:
   print(f"API error: {e.message}")
   print(f"Status code: {e.http_status_code}")
```

</div>

## Best Practices

1. **Client Usage**
   - Use the unified `ScmClient` approach for simpler code
   - Access security zone operations via `client.security_zone` property
   - Perform commit operations directly on the client
   - Monitor jobs directly on the client
   - Set appropriate max_limit parameters for large datasets using `security_zone_max_limit`

2. **Security Zone Configuration**
   - Use clear and descriptive names for security zones
   - Configure only one network interface type per zone
   - Follow the principle of least privilege for user and device access control lists
   - Enable user and device identification only when necessary for policy enforcement
   - Use proper zone protection profiles to secure network segments

3. **Network Type Selection**
   - Use **Layer 3** for most traditional routed networks
   - Use **Layer 2** when operating at the data link layer is required
   - Use **Virtual Wire** for transparent inline deployments
   - Use **TAP** for passive monitoring without affecting traffic flow
   - Use **Tunnel** for VPN and other tunnel-based connections
   - Use **External** for connecting to external networks

4. **Filtering and Container Parameters**
   - Always provide exactly one container parameter: `folder`, `snippet`, or `device`
   - Use the `exact_match` parameter if strict container matching is required
   - Leverage additional filters (e.g., `enable_user_identification`) for precise listings

5. **Error Handling**
   - Implement comprehensive error handling for invalid data and missing parameters
   - Handle model validation errors for network configurations
   - Log responses and exceptions to troubleshoot API issues effectively

6. **Performance**
   - Adjust the `max_limit` based on your environment and API rate limits
   - Utilize pagination effectively when working with large numbers of security zones

## Full Script Examples

Refer to the [security_zone.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/network/security_zone.py) for a complete implementation.

## Related Models

The security zone configuration uses several nested models for comprehensive validation:

- [SecurityZoneCreateModel](../../models/network/security_zone_models.md#securityzonecreatemodel) - For creating new security zones
- [SecurityZoneUpdateModel](../../models/network/security_zone_models.md#securityzoneupdatemodel) - For updating existing security zones
- [SecurityZoneResponseModel](../../models/network/security_zone_models.md#securityzoneresponsemodel) - For representing API responses
- [NetworkConfig](../../models/network/security_zone_models.md#networkconfig) - For configuring network interfaces and properties
- [UserAcl](../../models/network/security_zone_models.md#useracl) - For user access control lists
- [DeviceAcl](../../models/network/security_zone_models.md#deviceacl) - For device access control lists
