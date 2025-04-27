# Security Zone Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Security Zone Model Attributes](#security-zone-model-attributes)
4. [Network Interface Types](#network-interface-types)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating Security Zones](#creating-security-zones)
    - [Retrieving Security Zones](#retrieving-security-zones)
    - [Updating Security Zones](#updating-security-zones)
    - [Listing Security Zones](#listing-security-zones)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Security Zones](#deleting-security-zones)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Full Script Examples](#full-script-examples)
12. [Related Models](#related-models)

## Overview

The `SecurityZone` class manages security zone objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete security zones. Additionally, it provides client-side filtering for listing operations and enforces container requirements using the `folder`, `snippet`, or `device` parameters.

## Core Methods

| Method     | Description                                                   | Parameters                                                                                                                       | Return Type                       |
|------------|---------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| `create()` | Creates a new security zone object                            | `data: Dict[str, Any]`                                                                                                           | `SecurityZoneResponseModel`       |
| `get()`    | Retrieves a security zone object by its unique ID             | `object_id: str`                                                                                                                 | `SecurityZoneResponseModel`       |
| `update()` | Updates an existing security zone object                      | `zone: SecurityZoneUpdateModel`                                                                                                  | `SecurityZoneResponseModel`       |
| `list()`   | Lists security zone objects with optional filtering           | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[SecurityZoneResponseModel]` |
| `fetch()`  | Fetches a single security zone by its name within a container | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `SecurityZoneResponseModel`       |
| `delete()` | Deletes a security zone object by its ID                      | `object_id: str`                                                                                                                 | `None`                            |

## Security Zone Model Attributes

| Attribute                      | Type          | Required      | Description                                             |
|--------------------------------|---------------|---------------|---------------------------------------------------------|
| `name`                         | str           | Yes           | The name of the security zone                           |
| `id`                           | UUID          | Yes*          | Unique identifier (response only)                       |
| `enable_user_identification`   | bool          | No            | Enables user identification                             |
| `enable_device_identification` | bool          | No            | Enables device identification                           |
| `dos_profile`                  | str           | No            | Denial of Service profile name                          |
| `dos_log_setting`              | str           | No            | DoS log setting name                                    |
| `network`                      | NetworkConfig | No            | Network configuration for the zone                      |
| `user_acl`                     | UserAcl       | No            | User access control list configuration                  |
| `device_acl`                   | DeviceAcl     | No            | Device access control list configuration                |
| `folder`                       | str           | Conditionally | The folder container where the security zone is defined |
| `snippet`                      | str           | Conditionally | The snippet container (if applicable)                   |
| `device`                       | str           | Conditionally | The device container (if applicable)                    |

*\* The `id` field is assigned by the system and is only present in response objects.*

## Network Interface Types

Security zones can use different network interface types, following a mutual exclusion pattern where exactly one type must be provided:

### 1. Layer 3 Interfaces

Layer 3 interfaces are the most common type and define routed interfaces.

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

### 2. Layer 2 Interfaces

Layer 2 interfaces operate at the data link layer.

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

### 3. Virtual Wire Interfaces

Virtual wire interfaces connect two interfaces together.

```python
security_zone_data = {
   "name": "virtual-wire-zone",
   "network": {
      "virtual_wire": ["ethernet1/5", "ethernet1/6"]
   },
   "folder": "Security Zones"
}
```

### 4. Tunnel Interfaces

Tunnel interfaces are used for VPN and other tunneling technologies.

```python
security_zone_data = {
   "name": "tunnel-zone",
   "network": {
      "tunnel": {}  # Configuration depends on the tunnel type
   },
   "folder": "Security Zones"
}
```

### 5. TAP Interfaces

TAP interfaces are used for traffic monitoring without affecting the traffic flow.

```python
security_zone_data = {
   "name": "tap-zone",
   "network": {
      "tap": ["ethernet1/7"]
   },
   "folder": "Security Zones"
}
```

### 6. External Interfaces

External interfaces are used for connecting to external networks.

```python
security_zone_data = {
   "name": "external-zone",
   "network": {
      "external": ["ethernet1/8"]
   },
   "folder": "Security Zones"
}
```

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Security zone name already exists                                             |
| `ObjectNotPresentError`      | 404       | Security zone not found                                                       |
| `ReferenceNotZeroError`      | 409       | Security zone still referenced                                                |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Basic Configuration

The Security Zone service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the Security Zone service directly through the client
# No need to create a separate SecurityZone instance
# The ScmClient automatically handles authentication and token refresh
zones = client.security_zone
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import SecurityZone

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize SecurityZone object explicitly
zones = SecurityZone(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Security Zones

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

### Retrieving Security Zones

```python
# Fetch by name and folder
zone = client.security_zone.fetch(
   name="trust-zone",
   folder="Security Zones"
)
print(f"Found security zone: {zone.name}")

# Get by ID
zone_by_id = client.security_zone.get(zone.id)
print(f"Retrieved security zone: {zone_by_id.name}")
```

### Updating Security Zones

```python
# Fetch existing security zone
existing_zone = client.security_zone.fetch(
   name="trust-zone",
   folder="Security Zones"
)

# Update specific attributes
if existing_zone.network and existing_zone.network.layer3:
    # Add a new interface to the existing list
    existing_zone.network.layer3.append("ethernet1/3")

# Update protection profile
if existing_zone.network:
    existing_zone.network.zone_protection_profile = "enhanced-security"

# Update user identification setting
existing_zone.enable_device_identification = True

# Perform update
updated_zone = client.security_zone.update(existing_zone)
```

### Listing Security Zones

```python
# Pass filters directly into the list method
filtered_zones = client.security_zone.list(
    folder="Security Zones",
    enable_user_identification=True
)

# Process results
for zone in filtered_zones:
    print(f"Name: {zone.name}")

    # Check network configuration
    if zone.network:
        if zone.network.layer3:
            print(f"  Type: Layer 3, Interfaces: {', '.join(zone.network.layer3)}")
        elif zone.network.layer2:
            print(f"  Type: Layer 2, Interfaces: {', '.join(zone.network.layer2)}")
        # Check other network types...

    # Display user identification status
    print(f"  User ID Enabled: {zone.enable_user_identification}")
    print(f"  Device ID Enabled: {zone.enable_device_identification}")

# Define filter parameters as a dictionary
list_params = {
    "folder": "Security Zones",
    "enable_device_identification": False
}

# List zones with filters as kwargs
filtered_zones = client.security_zone.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters,
you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control
which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return security zones defined exactly in 'Security Zones'
exact_zones = client.security_zone.list(
   folder='Security Zones',
   exact_match=True
)

for zone in exact_zones:
   print(f"Exact match: {zone.name} in {zone.folder}")

# Exclude all security zones from the 'All' folder
no_all_zones = client.security_zone.list(
   folder='Security Zones',
   exclude_folders=['All']
)

for zone in no_all_zones:
   assert zone.folder != 'All'
   print(f"Filtered out 'All': {zone.name}")

# Exclude security zones that come from 'default' snippet
no_default_snippet = client.security_zone.list(
   folder='Security Zones',
   exclude_snippets=['default']
)

for zone in no_default_snippet:
   assert zone.snippet != 'default'
   print(f"Filtered out 'default' snippet: {zone.name}")

# Exclude security zones associated with 'DeviceA'
no_deviceA = client.security_zone.list(
   folder='Security Zones',
   exclude_devices=['DeviceA']
)

for zone in no_deviceA:
   assert zone.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {zone.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.security_zone.list(
   folder='Security Zones',
   exact_match=True,
   exclude_folders=['All'],
   exclude_snippets=['default'],
   exclude_devices=['DeviceA']
)

for zone in combined_filters:
   print(f"Combined filters result: {zone.name} in {zone.folder}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

```python
from scm.client import ScmClient
from scm.config.network import SecurityZone

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom SecurityZone instance with max_limit
security_zone_service = SecurityZone(client, max_limit=4321)
all_zones1 = security_zone_service.list(folder='Security Zones')

# Option 2: Use the unified client interface directly
# This will use the default max_limit (2500)
all_zones2 = client.security_zone.list(folder='Security Zones')

# Both options will auto-paginate through all available objects.
# The security zones are fetched in chunks according to the max_limit.
```

### Deleting Security Zones

```python
# Delete by ID
zone_id = "123e4567-e89b-12d3-a456-426655440000"
client.security_zone.delete(zone_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Security Zones"],
   "description": "Updated security zones",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
   print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import (
   InvalidObjectError,
   MissingQueryParameterError,
   NameNotUniqueError,
   ObjectNotPresentError,
   ReferenceNotZeroError
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create security zone configuration
   zone_config = {
      "name": "test-zone",
      "network": {
         "layer3": ["ethernet1/10"],
         "zone_protection_profile": "default"
      },
      "folder": "Security Zones",
      "description": "Test zone",
      "enable_user_identification": True
   }

   # Create the security zone using the unified client interface
   new_zone = client.security_zone.create(zone_config)

   # Commit changes directly from the client
   result = client.commit(
      folders=["Security Zones"],
      description="Added test security zone",
      sync=True
   )

   # Check job status directly from the client
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid security zone data: {e.message}")
except NameNotUniqueError as e:
   print(f"Security zone name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Security zone not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Security zone still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
   - Use the unified client interface (`client.security_zone`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)
   - For custom max_limit settings, create a dedicated service instance if needed

2. **Security Zone Configuration**
   - Choose appropriate network interface types for your deployment scenario
   - Use clear and descriptive names for security zones
   - Configure only one network interface type per zone
   - Enable user and device identification only when necessary for policy enforcement
   - Use proper zone protection profiles to secure network segments

3. **Container Management**
   - Always specify exactly one container (folder, snippet, or device)
   - Use consistent container names across operations
   - Validate container existence before operations
   - Group related zones logically

4. **Error Handling**
   - Implement comprehensive error handling for all operations
   - Check job status after commits
   - Handle specific exceptions before generic ones
   - Log error details for troubleshooting

5. **Performance**
   - Use appropriate pagination for list operations
   - Cache frequently accessed security zones
   - Implement proper retry mechanisms
   - Monitor timeout settings

6. **Security**
   - Follow the least privilege principle for zone configurations
   - Validate input data before operations
   - Document security implications
   - Monitor zone usage in security policies

## Full Script Examples

Refer to
the [security_zone.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/network/security_zone.py).

## Related Models

- [SecurityZoneCreateModel](../../models/network/security_zone_models.md#Overview)
- [SecurityZoneUpdateModel](../../models/network/security_zone_models.md#Overview)
- [SecurityZoneResponseModel](../../models/network/security_zone_models.md#Overview)
- [NetworkConfig](../../models/network/security_zone_models.md#Overview)
- [UserAcl](../../models/network/security_zone_models.md#Overview)
- [DeviceAcl](../../models/network/security_zone_models.md#Overview)
