# DHCP Interface Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [DHCP Interface Model Attributes](#dhcp-interface-model-attributes)
4. [Server and Relay Configuration](#server-and-relay-configuration)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating DHCP Interfaces](#creating-dhcp-interfaces)
    - [Retrieving DHCP Interfaces](#retrieving-dhcp-interfaces)
    - [Updating DHCP Interfaces](#updating-dhcp-interfaces)
    - [Listing DHCP Interfaces](#listing-dhcp-interfaces)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting DHCP Interfaces](#deleting-dhcp-interfaces)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `DhcpInterface` class manages DHCP server and relay configurations on firewall interfaces in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete DHCP interface configurations. Each DHCP interface can operate as either a DHCP server or a DHCP relay -- the two modes are mutually exclusive.

## Core Methods

| Method     | Description                                                       | Parameters                                                                                                                       | Return Type                          |
|------------|-------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| `create()` | Creates a new DHCP interface configuration                        | `data: Dict[str, Any]`                                                                                                           | `DhcpInterfaceResponseModel`         |
| `get()`    | Retrieves a DHCP interface configuration by its unique ID         | `object_id: str`                                                                                                                 | `DhcpInterfaceResponseModel`         |
| `update()` | Updates an existing DHCP interface configuration                  | `dhcp_interface: DhcpInterfaceUpdateModel`                                                                                       | `DhcpInterfaceResponseModel`         |
| `list()`   | Lists DHCP interface configurations with optional filtering       | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[DhcpInterfaceResponseModel]`   |
| `fetch()`  | Fetches a single DHCP interface by name within a container        | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `DhcpInterfaceResponseModel`         |
| `delete()` | Deletes a DHCP interface configuration by its ID                  | `object_id: str`                                                                                                                 | `None`                               |

## DHCP Interface Model Attributes

| Attribute  | Type       | Required      | Default | Description                                            |
|------------|------------|---------------|---------|--------------------------------------------------------|
| `name`     | str        | Yes           | None    | The interface name (e.g., `ethernet1/1`)               |
| `id`       | UUID       | Yes*          | None    | Unique identifier (*response/update only)              |
| `server`   | DhcpServer | No**          | None    | DHCP server configuration                              |
| `relay`    | DhcpRelay  | No**          | None    | DHCP relay configuration                               |
| `folder`   | str        | No***         | None    | Folder location. Max 64 chars                          |
| `snippet`  | str        | No***         | None    | Snippet location. Max 64 chars                         |
| `device`   | str        | No***         | None    | Device location. Max 64 chars                          |

\* Only required for update and response models
\** `server` and `relay` are mutually exclusive -- only one may be provided
\*** Exactly one container (folder/snippet/device) must be provided for create operations

## Server and Relay Configuration

### DHCP Server (DhcpServer)

The server configuration provides full DHCP server capabilities on an interface.

| Attribute  | Type               | Description                                     |
|------------|--------------------|-------------------------------------------------|
| `probe_ip` | bool              | Enable IP probe before assignment               |
| `mode`     | DhcpServerMode     | Server mode: `auto`, `enabled`, or `disabled`   |
| `option`   | DhcpServerOption   | Server options (lease, DNS, gateway, etc.)       |
| `ip_pool`  | List[str]          | List of IP pool ranges (e.g., `10.0.0.10-10.0.0.100`) |
| `reserved` | List[DhcpReserved] | Reserved address entries (name + MAC)           |

#### Server Options (DhcpServerOption)

| Attribute     | Type            | Description                        |
|---------------|-----------------|------------------------------------|
| `lease`       | DhcpLease       | Lease config (`unlimited` or `timeout` -- mutually exclusive) |
| `inheritance` | DhcpInheritance | Inheritance source                 |
| `gateway`     | str             | Gateway address                    |
| `subnet_mask` | str             | Subnet mask                        |
| `dns`         | DhcpDualServer  | DNS servers (primary + secondary)  |
| `wins`        | DhcpDualServer  | WINS servers (primary + secondary) |
| `nis`         | DhcpDualServer  | NIS servers (primary + secondary)  |
| `ntp`         | DhcpDualServer  | NTP servers (primary + secondary)  |
| `pop3_server` | str             | POP3 server address                |
| `smtp_server` | str             | SMTP server address                |
| `dns_suffix`  | str             | DNS suffix                         |

### DHCP Relay (DhcpRelay)

The relay configuration forwards DHCP requests to external DHCP servers.

| Attribute | Type        | Description                          |
|-----------|-------------|--------------------------------------|
| `ip`      | DhcpRelayIp | DHCP relay IP configuration          |

#### DhcpRelayIp

| Attribute | Type       | Description                              |
|-----------|------------|------------------------------------------|
| `enabled` | bool       | Enable DHCP relay (default: `True`)      |
| `server`  | List[str]  | List of DHCP relay server addresses      |

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | DHCP interface name already exists                                            |
| `ObjectNotPresentError`      | 404       | DHCP interface not found                                                      |
| `ReferenceNotZeroError`      | 409       | DHCP interface still referenced                                               |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Basic Configuration

The DHCP Interface service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the DHCP Interface service directly through the client
dhcp_interfaces = client.dhcp_interface
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import DhcpInterface

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize DhcpInterface object explicitly
dhcp_interfaces = DhcpInterface(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating DHCP Interfaces

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a DHCP server configuration on an interface
server_data = {
   "name": "ethernet1/1",
   "server": {
      "mode": "enabled",
      "probe_ip": True,
      "ip_pool": ["10.0.1.10-10.0.1.100"],
      "option": {
         "lease": {
            "timeout": 1440
         },
         "gateway": "10.0.1.1",
         "subnet_mask": "255.255.255.0",
         "dns": {
            "primary": "8.8.8.8",
            "secondary": "8.8.4.4"
         },
         "ntp": {
            "primary": "pool.ntp.org"
         },
         "dns_suffix": "example.com"
      },
      "reserved": [
         {
            "name": "10.0.1.50",
            "mac": "00:1a:2b:3c:4d:5e",
            "description": "Print server"
         }
      ]
   },
   "folder": "Texas"
}

new_server = client.dhcp_interface.create(server_data)
print(f"Created DHCP server on interface with ID: {new_server.id}")

# Create a DHCP relay configuration on an interface
relay_data = {
   "name": "ethernet1/2",
   "relay": {
      "ip": {
         "enabled": True,
         "server": ["10.0.0.1", "10.0.0.2"]
      }
   },
   "folder": "Texas"
}

new_relay = client.dhcp_interface.create(relay_data)
print(f"Created DHCP relay on interface with ID: {new_relay.id}")
```

### Retrieving DHCP Interfaces

```python
# Fetch by name and folder
dhcp_iface = client.dhcp_interface.fetch(
   name="ethernet1/1",
   folder="Texas"
)
print(f"Found DHCP interface: {dhcp_iface.name}")

# Get by ID
dhcp_by_id = client.dhcp_interface.get(dhcp_iface.id)
print(f"Retrieved DHCP interface: {dhcp_by_id.name}")
if dhcp_by_id.server:
   print(f"  Mode: {dhcp_by_id.server.mode}")
elif dhcp_by_id.relay:
   print("  Type: DHCP Relay")
```

### Updating DHCP Interfaces

```python
# Fetch existing DHCP interface
existing_dhcp = client.dhcp_interface.fetch(
   name="ethernet1/1",
   folder="Texas"
)

# Update the IP pool
if existing_dhcp.server:
   existing_dhcp.server.ip_pool = ["10.0.1.10-10.0.1.200"]

   # Update DNS settings
   if existing_dhcp.server.option and existing_dhcp.server.option.dns:
      existing_dhcp.server.option.dns.primary = "1.1.1.1"
      existing_dhcp.server.option.dns.secondary = "1.0.0.1"

# Perform update
updated_dhcp = client.dhcp_interface.update(existing_dhcp)
```

### Listing DHCP Interfaces

```python
# List all DHCP interfaces in a folder
dhcp_interfaces = client.dhcp_interface.list(
   folder="Texas"
)

# Process results
for iface in dhcp_interfaces:
   print(f"Interface: {iface.name}")
   if iface.server:
      print(f"  Type: DHCP Server (mode: {iface.server.mode})")
      if iface.server.ip_pool:
         print(f"  IP Pools: {', '.join(iface.server.ip_pool)}")
   elif iface.relay:
      print(f"  Type: DHCP Relay")
      if iface.relay.ip:
         print(f"  Relay Servers: {', '.join(iface.relay.ip.server)}")

# List with mode filter (filter by DHCP server mode)
auto_mode = client.dhcp_interface.list(
   folder="Texas",
   mode=["auto"]
)
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
# Only return DHCP interfaces defined exactly in 'Texas'
exact_dhcp = client.dhcp_interface.list(
   folder='Texas',
   exact_match=True
)

for iface in exact_dhcp:
   print(f"Exact match: {iface.name} in {iface.folder}")

# Exclude all DHCP interfaces from the 'All' folder
no_all_dhcp = client.dhcp_interface.list(
   folder='Texas',
   exclude_folders=['All']
)

for iface in no_all_dhcp:
   assert iface.folder != 'All'
   print(f"Filtered out 'All': {iface.name}")
```

### Controlling Pagination with max_limit

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
client.dhcp_interface.max_limit = 4000

# List all DHCP interfaces - auto-paginates through results
all_dhcp = client.dhcp_interface.list(folder='Texas')
```

### Deleting DHCP Interfaces

```python
# Delete by ID
dhcp_id = "123e4567-e89b-12d3-a456-426655440000"
client.dhcp_interface.delete(dhcp_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated DHCP interface configurations",
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
   # Create DHCP server configuration
   dhcp_config = {
      "name": "ethernet1/3",
      "server": {
         "mode": "enabled",
         "ip_pool": ["192.168.1.10-192.168.1.100"],
         "option": {
            "gateway": "192.168.1.1",
            "subnet_mask": "255.255.255.0",
            "dns": {
               "primary": "8.8.8.8"
            }
         }
      },
      "folder": "Texas"
   }

   # Create the DHCP interface using the unified client interface
   new_dhcp = client.dhcp_interface.create(dhcp_config)

   # Commit changes directly from the client
   result = client.commit(
      folders=["Texas"],
      description="Added DHCP server on ethernet1/3",
      sync=True
   )

   # Check job status directly from the client
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid DHCP interface data: {e.message}")
except NameNotUniqueError as e:
   print(f"DHCP interface already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"DHCP interface not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"DHCP interface still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
   - Use the unified client interface (`client.dhcp_interface`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **DHCP Configuration**
   - Choose either server or relay mode per interface -- they are mutually exclusive
   - Use DHCP server mode when the firewall should directly serve IP addresses
   - Use DHCP relay mode when forwarding requests to centralized DHCP servers
   - Always configure a `gateway` and `subnet_mask` in server options
   - Use IP reservations for critical infrastructure devices (servers, printers)

3. **Server Mode Best Practices**
   - Define appropriate IP pool ranges that do not overlap with static assignments
   - Set reasonable lease timeouts (avoid unlimited leases in dynamic environments)
   - Configure primary and secondary DNS servers for redundancy
   - Enable `probe_ip` to verify IP availability before assignment

4. **Container Management**
   - Always specify exactly one container (folder, snippet, or device)
   - Use consistent container names across operations
   - Validate container existence before operations

5. **Error Handling**
   - Implement comprehensive error handling for all operations
   - Check job status after commits
   - Handle specific exceptions before generic ones
   - Log error details for troubleshooting

6. **Performance**
   - Use appropriate pagination for list operations
   - Cache frequently accessed DHCP interface configurations
   - Implement proper retry mechanisms

## Related Models

- [DhcpInterfaceBaseModel](../../models/network/dhcp_interface_models.md#Overview)
- [DhcpInterfaceCreateModel](../../models/network/dhcp_interface_models.md#Overview)
- [DhcpInterfaceUpdateModel](../../models/network/dhcp_interface_models.md#Overview)
- [DhcpInterfaceResponseModel](../../models/network/dhcp_interface_models.md#Overview)
- [DhcpServer](../../models/network/dhcp_interface_models.md#Overview)
- [DhcpRelay](../../models/network/dhcp_interface_models.md#Overview)
