# IKE Gateway Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [IKE Gateway Model Attributes](#ike-gateway-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating IKE Gateway Objects](#creating-ike-gateway-objects)
    - [Retrieving IKE Gateways](#retrieving-ike-gateways)
    - [Updating IKE Gateways](#updating-ike-gateways)
    - [Listing IKE Gateways](#listing-ike-gateways)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting IKE Gateways](#deleting-ike-gateways)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Related Models](#related-models)

## Overview

The `IKEGateway` class provides functionality to manage Internet Key Exchange (IKE) gateway objects in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting IKE gateway configurations used for establishing VPN tunnels.

## Core Methods

| Method     | Description                        | Parameters                       | Return Type                 |
|------------|------------------------------------|----------------------------------|----------------------------|
| `create()` | Creates a new IKE gateway          | `data: Dict[str, Any]`          | `IKEGatewayResponseModel`  |
| `get()`    | Retrieves an IKE gateway by ID     | `object_id: str`                | `IKEGatewayResponseModel`  |
| `update()` | Updates an existing IKE gateway    | `gateway: IKEGatewayUpdateModel`| `IKEGatewayResponseModel`  |
| `delete()` | Deletes an IKE gateway             | `object_id: str`                | `None`                     |
| `list()`   | Lists IKE gateways with filtering  | `folder: str`, `**filters`      | `List[IKEGatewayResponseModel]` |
| `fetch()`  | Gets IKE gateway by name and container | `name: str`, `folder: str`  | `IKEGatewayResponseModel`  |

## IKE Gateway Model Attributes

| Attribute          | Type       | Required     | Description                                  |
|--------------------|------------|--------------|----------------------------------------------|
| `name`             | str        | Yes          | Name of IKE gateway (max 63 chars)          |
| `id`               | UUID       | Yes*         | Unique identifier (*response only)           |
| `authentication`   | dict       | Yes          | Authentication configuration (pre-shared key or certificate) |
| `peer_id`          | dict       | No           | Peer identification information              |
| `local_id`         | dict       | No           | Local identification information             |
| `protocol`         | dict       | Yes          | IKE protocol configuration                   |
| `protocol_common`  | dict       | No           | Common protocol settings                     |
| `peer_address`     | dict       | Yes          | Peer address configuration (IP, FQDN, or dynamic) |
| `folder`           | str        | Yes**        | Folder location (**one container required)   |
| `snippet`          | str        | Yes**        | Snippet location (**one container required)  |
| `device`           | str        | Yes**        | Device location (**one container required)   |

## Exceptions

| Exception                    | HTTP Code | Description                          |
|------------------------------|-----------|--------------------------------------|
| `InvalidObjectError`         | 400       | Invalid IKE gateway data or format   |
| `MissingQueryParameterError` | 400       | Missing required parameters          |
| `NameNotUniqueError`         | 409       | IKE gateway name already exists      |
| `ObjectNotPresentError`      | 404       | IKE gateway not found                |
| `ReferenceNotZeroError`      | 409       | IKE gateway still referenced         |
| `AuthenticationError`        | 401       | Authentication failed                |
| `ServerError`                | 500       | Internal server error                |

## Basic Configuration

The IKE Gateway service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

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

# Access the IKE Gateway service directly through the client
# No need to create a separate IKEGateway instance
ike_gateways = client.ike_gateway
```

</div>

### Traditional Service Instantiation (Legacy)

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.network import IKEGateway

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize IKEGateway object explicitly
ike_gateways = IKEGateway(client)
```

</div>

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating IKE Gateway Objects

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

# Prepare IKE Gateway configuration with pre-shared key
psk_config = {
   "name": "site-a-gateway",
   "authentication": {
       "pre_shared_key": {
           "key": "your-secure-key"
       }
   },
   "peer_id": {
       "type": "ipaddr",
       "id": "203.0.113.1"
   },
   "protocol": {
       "version": "ikev2",
       "ikev2": {
           "ike_crypto_profile": "default",
           "dpd": {
               "enable": True
           }
       }
   },
   "peer_address": {
       "ip": "203.0.113.1"
   },
   "folder": "VPN"
}

# Create the IKE gateway object
psk_gateway = client.ike_gateway.create(psk_config)

# Prepare IKE Gateway with certificate authentication
cert_config = {
   "name": "site-b-gateway",
   "authentication": {
       "certificate": {
           "certificate_profile": "default-profile",
           "local_certificate": {
               "local_certificate_name": "cert-name"
           }
       }
   },
   "protocol": {
       "version": "ikev2-preferred",
       "ikev1": {
           "ike_crypto_profile": "default"
       },
       "ikev2": {
           "ike_crypto_profile": "default"
       }
   },
   "peer_address": {
       "fqdn": "vpn.example.com"
   },
   "folder": "VPN"
}

# Create the certificate-based IKE gateway
cert_gateway = client.ike_gateway.create(cert_config)
```

</div>

### Retrieving IKE Gateways

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
gateway = client.ike_gateway.fetch(name="site-a-gateway", folder="VPN")
print(f"Found gateway: {gateway.name}")

# Get by ID
gateway_by_id = client.ike_gateway.get(gateway.id)
print(f"Retrieved gateway: {gateway_by_id.name}")
```

</div>

### Updating IKE Gateways

<div class="termy">

<!-- termynal -->

```python
# Fetch existing IKE gateway
existing_gateway = client.ike_gateway.fetch(name="site-a-gateway", folder="VPN")

# Create an update model with new values
from scm.models.network import IKEGatewayUpdateModel

# Update specific attributes
update_data = {
    "id": str(existing_gateway.id),
    "name": existing_gateway.name,
    "peer_id": {
        "type": "ipaddr",
        "id": "203.0.113.2"  # Updated peer ID
    },
    "protocol_common": {
        "nat_traversal": {
            "enable": True
        }
    }
}

# Create update model
gateway_update = IKEGatewayUpdateModel(**update_data)

# Perform update
updated_gateway = client.ike_gateway.update(gateway_update)
```

</div>

### Listing IKE Gateways

<div class="termy">

<!-- termynal -->

```python
# List all IKE gateways in a folder
gateways = client.ike_gateway.list(folder="VPN")

# Process results
for gateway in gateways:
   print(f"Name: {gateway.name}, Peer Address: {gateway.peer_address.ip if hasattr(gateway.peer_address, 'ip') else gateway.peer_address.fqdn if hasattr(gateway.peer_address, 'fqdn') else 'dynamic'}")

# Exclude inherited gateways (only show gateways defined directly in the folder)
direct_gateways = client.ike_gateway.list(
    folder="VPN",
    exact_match=True
)

print(f"Found {len(direct_gateways)} gateways defined directly in VPN folder")
```

</div>

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. You can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

<div class="termy">

<!-- termynal -->

```python
# Only return IKE gateways defined exactly in 'VPN'
exact_gateways = client.ike_gateway.list(
   folder='VPN',
   exact_match=True
)

for gateway in exact_gateways:
   print(f"Exact match: {gateway.name} in {gateway.folder}")

# Exclude all IKE gateways from the 'Shared' folder
no_shared_gateways = client.ike_gateway.list(
   folder='VPN',
   exclude_folders=['Shared']
)

for gateway in no_shared_gateways:
   assert gateway.folder != 'Shared'
   print(f"Filtered out 'Shared': {gateway.name}")

# Exclude gateways that come from 'default' snippet
no_default_snippet = client.ike_gateway.list(
   folder='VPN',
   exclude_snippets=['default']
)

for gateway in no_default_snippet:
   assert gateway.snippet != 'default'
   print(f"Filtered out 'default' snippet: {gateway.name}")

# Exclude gateways associated with 'DeviceA'
no_deviceA = client.ike_gateway.list(
   folder='VPN',
   exclude_devices=['DeviceA']
)

for gateway in no_deviceA:
   assert gateway.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {gateway.name}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient
from scm.config.network import IKEGateway

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom IKEGateway instance with max_limit
ike_gateway_service = IKEGateway(client, max_limit=4000)
all_gateways1 = ike_gateway_service.list(folder='VPN')

# Option 2: Use the unified client interface directly
# This will use the default max_limit (2500)
all_gateways2 = client.ike_gateway.list(folder='VPN')

# Both options will auto-paginate through all available objects.
# The gateways are fetched in chunks according to the max_limit.
```

</div>

### Deleting IKE Gateways

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
gateway_id = "123e4567-e89b-12d3-a456-426655440000"
client.ike_gateway.delete(gateway_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
   "folders": ["VPN"],
   "description": "Added new IKE gateway configurations",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
     print(f"Job {job.id}: {job.type_str} - {job.status_str}")
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
   NameNotUniqueError,
   ObjectNotPresentError
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create IKE gateway configuration
   gateway_config = {
      "name": "test-gateway",
      "authentication": {
          "pre_shared_key": {
              "key": "secure-key"
          }
      },
      "protocol": {
          "version": "ikev2",
          "ikev2": {
              "ike_crypto_profile": "default"
          }
      },
      "peer_address": {
          "ip": "203.0.113.1"
      },
      "folder": "VPN"
   }
   
   # Create the IKE gateway using the unified client interface
   new_gateway = client.ike_gateway.create(gateway_config)
   
   # Commit changes directly from the client
   result = client.commit(
      folders=["VPN"],
      description="Added test gateway",
      sync=True
   )
   
   # Check job status directly from the client
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid gateway data: {e.message}")
except NameNotUniqueError as e:
   print(f"Gateway name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Gateway not found: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.ike_gateway`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names across operations
    - Validate container existence before operations

3. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

4. **Authentication Configuration**
    - Specify exactly one authentication method (pre-shared key or certificate)
    - Use strong pre-shared keys if using PSK authentication
    - Validate certificate existence when using certificate authentication
    - Consider security implications when storing authentication information

5. **Protocol Configuration**
    - Ensure protocol version matches supported IKE crypto profiles
    - Consider IKEv2 for newer deployments for better security
    - Properly configure dead peer detection (DPD) for tunnel health monitoring
    - Verify NAT traversal settings match your network environment

6. **Performance**
    - Reuse client instances
    - Use appropriate pagination for list operations
    - Implement proper retry mechanisms
    - Cache frequently accessed objects

7. **Security**
    - Follow the least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication handling
    - Never hardcode pre-shared keys in scripts

## Related Models

- [IKEGatewayCreateModel](../../models/network/ike_gateway_models.md#Overview)
- [IKEGatewayUpdateModel](../../models/network/ike_gateway_models.md#Overview)
- [IKEGatewayResponseModel](../../models/network/ike_gateway_models.md#Overview)
- [IKE Crypto Profile](ike_crypto_profile.md) - Related configuration for IKE crypto profiles