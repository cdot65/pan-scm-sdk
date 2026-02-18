# IPsec Tunnel Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [IPsec Tunnel Model Attributes](#ipsec-tunnel-model-attributes)
4. [Auto Key Configuration](#auto-key-configuration)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating IPsec Tunnels](#creating-ipsec-tunnels)
    - [Retrieving IPsec Tunnels](#retrieving-ipsec-tunnels)
    - [Updating IPsec Tunnels](#updating-ipsec-tunnels)
    - [Listing IPsec Tunnels](#listing-ipsec-tunnels)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting IPsec Tunnels](#deleting-ipsec-tunnels)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `IPsecTunnel` class manages IPsec tunnel objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete IPsec tunnels. IPsec tunnels provide encrypted connectivity between sites and complete the VPN stack alongside the existing IKE Gateway and IPsec Crypto Profile services. Each tunnel requires an `auto_key` configuration that references one or more IKE gateways and an IPsec crypto profile.

## Core Methods

| Method     | Description                                                     | Parameters                                                                                                                       | Return Type                        |
|------------|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| `create()` | Creates a new IPsec tunnel                                      | `data: Dict[str, Any]`                                                                                                           | `IPsecTunnelResponseModel`         |
| `get()`    | Retrieves an IPsec tunnel by its unique ID                      | `object_id: str`                                                                                                                 | `IPsecTunnelResponseModel`         |
| `update()` | Updates an existing IPsec tunnel                                | `tunnel: IPsecTunnelUpdateModel`                                                                                                 | `IPsecTunnelResponseModel`         |
| `list()`   | Lists IPsec tunnels with optional filtering                     | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[IPsecTunnelResponseModel]`   |
| `fetch()`  | Fetches a single IPsec tunnel by name within a container        | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `IPsecTunnelResponseModel`         |
| `delete()` | Deletes an IPsec tunnel by its ID                               | `object_id: str`                                                                                                                 | `None`                             |

## IPsec Tunnel Model Attributes

| Attribute                   | Type           | Required | Default | Description                                         |
|-----------------------------|----------------|----------|---------|-----------------------------------------------------|
| `name`                      | str            | Yes      | None    | Tunnel name. Max 63 chars                           |
| `id`                        | UUID           | Yes*     | None    | Unique identifier (*response/update only)           |
| `auto_key`                  | AutoKey        | Yes      | None    | Auto key configuration (IKE gateway + crypto profile) |
| `anti_replay`               | bool           | No       | None    | Enable anti-replay protection                       |
| `copy_tos`                  | bool           | No       | False   | Copy TOS header                                     |
| `enable_gre_encapsulation`  | bool           | No       | False   | Enable GRE encapsulation                            |
| `tunnel_monitor`            | TunnelMonitor  | No       | None    | Tunnel monitor configuration                        |
| `folder`                    | str            | No**     | None    | Folder location. Max 64 chars                       |
| `snippet`                   | str            | No**     | None    | Snippet location. Max 64 chars                      |
| `device`                    | str            | No**     | None    | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## Auto Key Configuration

The `auto_key` attribute is required for all IPsec tunnels and contains the IKE gateway references and crypto profile settings.

### AutoKey

| Attribute              | Type                | Required | Description                              |
|------------------------|---------------------|----------|------------------------------------------|
| `ike_gateway`          | List[IkeGatewayRef] | Yes      | List of IKE gateway references           |
| `ipsec_crypto_profile` | str                 | Yes      | IPsec crypto profile name                |
| `proxy_id`             | List[ProxyId]       | No       | List of proxy IDs                        |
| `proxy_id_v6`          | List[ProxyId]       | No       | List of IPv6 proxy IDs                   |

### IkeGatewayRef

| Attribute | Type | Required | Description                    |
|-----------|------|----------|--------------------------------|
| `name`    | str  | Yes      | The name of the IKE gateway    |

### ProxyId

| Attribute  | Type            | Required | Description                     |
|------------|-----------------|----------|---------------------------------|
| `name`     | str             | Yes      | The name of the proxy ID        |
| `local`    | str             | No       | Local address or subnet         |
| `remote`   | str             | No       | Remote address or subnet        |
| `protocol` | ProxyIdProtocol | No       | Protocol configuration          |

### TunnelMonitor

| Attribute        | Type | Required | Default | Description                                |
|------------------|------|----------|---------|--------------------------------------------|
| `enable`         | bool | No       | True    | Enable tunnel monitoring                   |
| `destination_ip` | str  | Yes      | None    | Destination IP for tunnel monitoring       |
| `proxy_id`       | str  | No       | None    | Proxy ID for tunnel monitoring             |

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Tunnel name already exists                                                    |
| `ObjectNotPresentError`      | 404       | Tunnel not found                                                              |
| `ReferenceNotZeroError`      | 409       | Tunnel still referenced                                                       |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Basic Configuration

The IPsec Tunnel service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the IPsec Tunnel service directly through the client
ipsec_tunnels = client.ipsec_tunnel
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import IPsecTunnel

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize IPsecTunnel object explicitly
ipsec_tunnels = IPsecTunnel(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating IPsec Tunnels

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a basic IPsec tunnel
tunnel_data = {
   "name": "site-a-to-site-b",
   "auto_key": {
      "ike_gateway": [
         {"name": "gw-site-b"}
      ],
      "ipsec_crypto_profile": "aes256-sha256"
   },
   "anti_replay": True,
   "folder": "Texas"
}

new_tunnel = client.ipsec_tunnel.create(tunnel_data)
print(f"Created IPsec tunnel with ID: {new_tunnel.id}")

# Create an IPsec tunnel with proxy IDs and tunnel monitoring
advanced_tunnel_data = {
   "name": "hq-to-branch",
   "auto_key": {
      "ike_gateway": [
         {"name": "gw-branch-office"}
      ],
      "ipsec_crypto_profile": "suite-b-gcm-256",
      "proxy_id": [
         {
            "name": "proxy-1",
            "local": "10.0.0.0/24",
            "remote": "192.168.1.0/24",
            "protocol": {
               "number": 0
            }
         }
      ]
   },
   "anti_replay": True,
   "copy_tos": True,
   "tunnel_monitor": {
      "enable": True,
      "destination_ip": "192.168.1.1"
   },
   "folder": "Texas"
}

advanced_tunnel = client.ipsec_tunnel.create(advanced_tunnel_data)
print(f"Created advanced IPsec tunnel with ID: {advanced_tunnel.id}")

# Create an IPsec tunnel with GRE encapsulation
gre_tunnel_data = {
   "name": "gre-over-ipsec",
   "auto_key": {
      "ike_gateway": [
         {"name": "gw-remote"}
      ],
      "ipsec_crypto_profile": "aes128-sha1"
   },
   "enable_gre_encapsulation": True,
   "folder": "Texas"
}

gre_tunnel = client.ipsec_tunnel.create(gre_tunnel_data)
print(f"Created GRE-over-IPsec tunnel with ID: {gre_tunnel.id}")
```

### Retrieving IPsec Tunnels

```python
# Fetch by name and folder
tunnel = client.ipsec_tunnel.fetch(
   name="site-a-to-site-b",
   folder="Texas"
)
print(f"Found tunnel: {tunnel.name}")
print(f"  IKE Gateway: {tunnel.auto_key.ike_gateway[0].name}")
print(f"  Crypto Profile: {tunnel.auto_key.ipsec_crypto_profile}")

# Get by ID
tunnel_by_id = client.ipsec_tunnel.get(tunnel.id)
print(f"Retrieved tunnel: {tunnel_by_id.name}")
```

### Updating IPsec Tunnels

```python
# Fetch existing tunnel
existing_tunnel = client.ipsec_tunnel.fetch(
   name="site-a-to-site-b",
   folder="Texas"
)

# Enable anti-replay and tunnel monitoring
existing_tunnel.anti_replay = True
existing_tunnel.tunnel_monitor = {
   "enable": True,
   "destination_ip": "10.1.1.1"
}

# Update crypto profile
existing_tunnel.auto_key.ipsec_crypto_profile = "suite-b-gcm-256"

# Perform update
updated_tunnel = client.ipsec_tunnel.update(existing_tunnel)
```

### Listing IPsec Tunnels

```python
# List all IPsec tunnels in a folder
tunnels = client.ipsec_tunnel.list(
   folder="Texas"
)

# Process results
for tunnel in tunnels:
   print(f"Name: {tunnel.name}")
   print(f"  IKE Gateway(s): {', '.join(gw.name for gw in tunnel.auto_key.ike_gateway)}")
   print(f"  Crypto Profile: {tunnel.auto_key.ipsec_crypto_profile}")
   print(f"  Anti-Replay: {tunnel.anti_replay}")
   if tunnel.tunnel_monitor:
      print(f"  Tunnel Monitor: {tunnel.tunnel_monitor.destination_ip}")

# List with crypto profile filter
filtered_tunnels = client.ipsec_tunnel.list(
   folder="Texas",
   ipsec_crypto_profile=["aes256-sha256", "suite-b-gcm-256"]
)

for tunnel in filtered_tunnels:
   print(f"Filtered tunnel: {tunnel.name} ({tunnel.auto_key.ipsec_crypto_profile})")
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
# Only return tunnels defined exactly in 'Texas'
exact_tunnels = client.ipsec_tunnel.list(
   folder='Texas',
   exact_match=True
)

for tunnel in exact_tunnels:
   print(f"Exact match: {tunnel.name} in {tunnel.folder}")

# Exclude all tunnels from the 'All' folder
no_all_tunnels = client.ipsec_tunnel.list(
   folder='Texas',
   exclude_folders=['All']
)

for tunnel in no_all_tunnels:
   assert tunnel.folder != 'All'
   print(f"Filtered out 'All': {tunnel.name}")
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
client.ipsec_tunnel.max_limit = 4000

# List all tunnels - auto-paginates through results
all_tunnels = client.ipsec_tunnel.list(folder='Texas')
```

### Deleting IPsec Tunnels

```python
# Delete by ID
tunnel_id = "123e4567-e89b-12d3-a456-426655440000"
client.ipsec_tunnel.delete(tunnel_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated IPsec tunnel configurations",
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
   # Create IPsec tunnel configuration
   tunnel_config = {
      "name": "test-tunnel",
      "auto_key": {
         "ike_gateway": [
            {"name": "test-gateway"}
         ],
         "ipsec_crypto_profile": "aes256-sha256"
      },
      "anti_replay": True,
      "folder": "Texas"
   }

   # Create the tunnel using the unified client interface
   new_tunnel = client.ipsec_tunnel.create(tunnel_config)

   # Commit changes directly from the client
   result = client.commit(
      folders=["Texas"],
      description="Added test IPsec tunnel",
      sync=True
   )

   # Check job status directly from the client
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid tunnel data: {e.message}")
except NameNotUniqueError as e:
   print(f"Tunnel name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Tunnel not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Tunnel still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
   - Use the unified client interface (`client.ipsec_tunnel`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **VPN Stack Configuration**
   - Create IKE crypto profiles and IPsec crypto profiles before creating tunnels
   - Configure IKE gateways before referencing them in IPsec tunnels
   - Use descriptive tunnel names that identify the connection endpoints
   - Follow the VPN configuration order: IKE Crypto Profile -> IPsec Crypto Profile -> IKE Gateway -> IPsec Tunnel

3. **Tunnel Configuration**
   - Always enable `anti_replay` for security against replay attacks
   - Use tunnel monitoring to detect and recover from tunnel failures
   - Configure proxy IDs when connecting to third-party VPN devices
   - Use GRE encapsulation only when routing protocols need to run over the tunnel
   - Set `copy_tos` when QoS preservation across the tunnel is required

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
   - Cache frequently accessed tunnel configurations
   - Implement proper retry mechanisms

7. **Security**
   - Use strong crypto profiles (AES-256, SHA-256 or better)
   - Regularly rotate IKE and IPsec keys
   - Monitor tunnel status for unexpected disconnections
   - Review and audit tunnel configurations periodically

## Related Models

- [IPsecTunnelBaseModel](../../models/network/ipsec_tunnel_models.md#Overview)
- [IPsecTunnelCreateModel](../../models/network/ipsec_tunnel_models.md#Overview)
- [IPsecTunnelUpdateModel](../../models/network/ipsec_tunnel_models.md#Overview)
- [IPsecTunnelResponseModel](../../models/network/ipsec_tunnel_models.md#Overview)
- [AutoKey](../../models/network/ipsec_tunnel_models.md#Overview)
- [IkeGatewayRef](../../models/network/ipsec_tunnel_models.md#Overview)
- [ProxyId](../../models/network/ipsec_tunnel_models.md#Overview)
- [TunnelMonitor](../../models/network/ipsec_tunnel_models.md#Overview)
