# Security Zone

The `SecurityZone` class manages security zone objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete security zones. Additionally, it provides client-side filtering for listing operations and enforces container requirements using the `folder`, `snippet`, or `device` parameters.

## Class Overview

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

| Method     | Description                                                   | Parameters                                                                                                                       | Return Type                       |
|------------|---------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| `create()` | Creates a new security zone object                            | `data: Dict[str, Any]`                                                                                                           | `SecurityZoneResponseModel`       |
| `get()`    | Retrieves a security zone object by its unique ID             | `object_id: str`                                                                                                                 | `SecurityZoneResponseModel`       |
| `update()` | Updates an existing security zone object                      | `zone: SecurityZoneUpdateModel`                                                                                                  | `SecurityZoneResponseModel`       |
| `list()`   | Lists security zone objects with optional filtering           | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[SecurityZoneResponseModel]` |
| `fetch()`  | Fetches a single security zone by its name within a container | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `SecurityZoneResponseModel`       |
| `delete()` | Deletes a security zone object by its ID                      | `object_id: str`                                                                                                                 | `None`                            |

### Security Zone Model Attributes

| Attribute                      | Type          | Required      | Default | Description                                             |
|--------------------------------|---------------|---------------|---------|--------------------------------------------------------|
| `name`                         | str           | Yes           | None    | Name of security zone. Max 63 chars. Pattern: `^[0-9a-zA-Z._\- ]+$` |
| `id`                           | UUID          | Yes*          | None    | Unique identifier (*response/update only)              |
| `enable_user_identification`   | bool          | No            | None    | Enables user identification                            |
| `enable_device_identification` | bool          | No            | None    | Enables device identification                          |
| `dos_profile`                  | str           | No            | None    | Denial of Service profile name                         |
| `dos_log_setting`              | str           | No            | None    | DoS log setting name                                   |
| `network`                      | NetworkConfig | No            | None    | Network configuration for the zone                     |
| `user_acl`                     | UserAcl       | No            | None    | User access control list configuration                 |
| `device_acl`                   | DeviceAcl     | No            | None    | Device access control list configuration               |
| `folder`                       | str           | No**          | None    | Folder location. Max 64 chars                          |
| `snippet`                      | str           | No**          | None    | Snippet location. Max 64 chars                         |
| `device`                       | str           | No**          | None    | Device location. Max 64 chars                          |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

### Network Interface Types

Security zones can use different network interface types, following a mutual exclusion pattern where exactly one type must be provided:

#### 1. Layer 3 Interfaces

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

#### 2. Layer 2 Interfaces

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

#### 3. Virtual Wire Interfaces

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

#### 4. Tunnel Interfaces

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

#### 5. TAP Interfaces

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

#### 6. External Interfaces

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

### Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Security zone name already exists                                             |
| `ObjectNotPresentError`      | 404       | Security zone not found                                                       |
| `ReferenceNotZeroError`      | 409       | Security zone still referenced                                                |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Methods

### List Security Zones

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

#### Filtering Responses

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

#### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.security_zone.max_limit = 4000

# List all security zones - auto-paginates through results
all_zones = client.security_zone.list(folder='Security Zones')

# The security zones are fetched in chunks according to the max_limit setting.
```

### Fetch a Security Zone

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

### Create a Security Zone

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

### Update a Security Zone

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

### Delete a Security Zone

```python
# Delete by ID
zone_id = "123e4567-e89b-12d3-a456-426655440000"
client.security_zone.delete(zone_id)
```

## Use Cases

#### Performing Commits

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

#### Monitoring Jobs

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

## Related Topics

- [SecurityZoneBaseModel](../../models/network/security_zone_models.md#Overview)
- [SecurityZoneCreateModel](../../models/network/security_zone_models.md#Overview)
- [SecurityZoneUpdateModel](../../models/network/security_zone_models.md#Overview)
- [SecurityZoneResponseModel](../../models/network/security_zone_models.md#Overview)
- [NetworkConfig](../../models/network/security_zone_models.md#Overview)
- [UserAcl](../../models/network/security_zone_models.md#Overview)
- [DeviceAcl](../../models/network/security_zone_models.md#Overview)
- [NetworkInterfaceType](../../models/network/security_zone_models.md#Overview)

Refer to
the [security_zone.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/network/security_zone.py).
