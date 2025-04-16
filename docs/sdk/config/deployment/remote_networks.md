# Remote Networks Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Remote Network Model Attributes](#remote-network-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Remote Networks](#creating-remote-networks)
    - [Retrieving Remote Networks](#retrieving-remote-networks)
    - [Updating Remote Networks](#updating-remote-networks)
    - [Listing Remote Networks](#listing-remote-networks)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Remote Networks](#deleting-remote-networks)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `RemoteNetworks` class provides functionality to manage remote network configurations in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting remote network configurations with support for both standard and ECMP-enabled setups.

## Core Methods

| Method     | Description                        | Parameters                                 | Return Type                        |
|------------|------------------------------------|--------------------------------------------|------------------------------------|
| `create()` | Creates a new remote network       | `data: Dict[str, Any]`                     | `RemoteNetworkResponseModel`       |
| `get()`    | Retrieves a network by ID          | `object_id: str`                           | `RemoteNetworkResponseModel`       |
| `update()` | Updates an existing network        | `remote_network: RemoteNetworkUpdateModel` | `RemoteNetworkResponseModel`       |
| `delete()` | Deletes a network                  | `object_id: str`                           | `None`                             |
| `list()`   | Lists networks with filtering      | `folder: str`, `**filters`                 | `List[RemoteNetworkResponseModel]` |
| `fetch()`  | Gets network by name and container | `name: str`, `folder: str`                 | `RemoteNetworkResponseModel`       |

## Remote Network Model Attributes

| Attribute             | Type          | Required | Description                                  |
|-----------------------|---------------|----------|----------------------------------------------|
| `name`                | str           | Yes      | Name of network (max 63 chars)               |
| `id`                  | UUID          | Yes*     | Unique identifier (*response only)           |
| `region`              | str           | Yes      | AWS region for deployment                    |
| `license_type`        | str           | Yes      | License type (default: FWAAS-AGGREGATE)      |
| `spn_name`            | str           | Yes**    | Service Provider Name (**required for FWAAS) |
| `description`         | str           | No       | Description (max 1023 chars)                 |
| `subnets`             | List[str]     | No       | List of network subnets                      |
| `ecmp_load_balancing` | str           | Yes      | ECMP mode (enable/disable)                   |
| `ecmp_tunnels`        | List[Dict]    | Yes***   | ECMP tunnel configs (***if ECMP enabled)     |
| `ipsec_tunnel`        | str           | Yes***   | IPSec tunnel name (***if ECMP disabled)      |
| `protocol`            | ProtocolModel | No       | BGP protocol configuration                   |
| `folder`              | str           | Yes      | Folder location                              |

## Exceptions

| Exception                    | HTTP Code | Description                    |
|------------------------------|-----------|--------------------------------|
| `InvalidObjectError`         | 400       | Invalid network data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters    |
| `NameNotUniqueError`         | 409       | Network name already exists    |
| `ObjectNotPresentError`      | 404       | Network not found              |
| `ReferenceNotZeroError`      | 409       | Network still referenced       |
| `AuthenticationError`        | 401       | Authentication failed          |
| `ServerError`                | 500       | Internal server error          |

## Basic Configuration

The Remote Networks service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Remote Networks service directly through the client
# No need to create a separate RemoteNetworks instance
networks = client.remote_networks
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.deployment import RemoteNetworks

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize RemoteNetworks object explicitly
networks = RemoteNetworks(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Remote Networks

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Standard remote network configuration
standard_config = {
    "name": "branch-office-1",
    "region": "us-east-1",
    "license_type": "FWAAS-AGGREGATE",
    "spn_name": "us-east-1-spn",
    "folder": "Remote Networks",
    "description": "Branch office VPN connection",
    "subnets": ["10.0.0.0/24", "10.0.1.0/24"],
    "ecmp_load_balancing": "disable",
    "ipsec_tunnel": "branch-1-tunnel"
}

# Create standard remote network
standard_network = client.remote_networks.create(standard_config)

# ECMP-enabled remote network configuration
ecmp_config = {
    "name": "branch-office-2",
    "region": "us-west-2",
    "license_type": "FWAAS-AGGREGATE",
    "spn_name": "us-west-2-spn",
    "folder": "Remote Networks",
    "description": "Branch office with ECMP",
    "subnets": ["172.16.0.0/24", "172.16.1.0/24"],
    "ecmp_load_balancing": "enable",
    "ecmp_tunnels": [
        {
            "name": "tunnel-1",
            "ipsec_tunnel": "branch-2-tunnel-1",
            "local_ip_address": "10.0.1.1",
            "peer_as": "65515",
            "peer_ip_address": "10.0.1.2"
        },
        {
            "name": "tunnel-2",
            "ipsec_tunnel": "branch-2-tunnel-2",
            "local_ip_address": "10.0.2.1",
            "peer_as": "65515",
            "peer_ip_address": "10.0.2.2"
        }
    ]
}

# Create ECMP-enabled remote network
ecmp_network = client.remote_networks.create(ecmp_config)
```

### Retrieving Remote Networks

```python
# Fetch by name and folder
network = client.remote_networks.fetch(
    name="branch-office-1",
    folder="Remote Networks"
)
print(f"Found network: {network.name}")

# Get by ID
network_by_id = client.remote_networks.get(network.id)
print(f"Retrieved network: {network_by_id.name}")
print(f"Subnets: {', '.join(network_by_id.subnets)}")
```

### Updating Remote Networks

```python
# Fetch existing network
existing_network = client.remote_networks.fetch(
    name="branch-office-1",
    folder="Remote Networks"
)

# Update attributes
existing_network.description = "Updated branch office configuration"
existing_network.subnets = ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]

# Add BGP configuration
existing_network.protocol = {
    "bgp": {
        "enable": True,
        "peer_as": "65515",
        "peer_ip_address": "10.0.0.1",
        "local_ip_address": "10.0.0.2"
    }
}

# Perform update
updated_network = client.remote_networks.update(existing_network)
```

### Listing Remote Networks

```python
# Pass filters directly into the list method
filtered_networks = client.remote_networks.list(
    folder='Remote Networks',
    regions=['us-east-1'],
    license_types=['FWAAS-AGGREGATE']
)

# Process results
for network in filtered_networks:
    print(f"Name: {network.name}")
    print(f"Region: {network.region}")
    print(f"Subnets: {', '.join(network.subnets)}")

# Define filter parameters as a dictionary
list_params = {
    "folder": "Remote Networks",
    "regions": ["us-west-2"],
    "spn_names": ["us-west-2-spn"]
}

# List with filters as kwargs
filtered_networks = client.remote_networks.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `regions`, `license_types`, and `spn_names`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return remote networks defined exactly in 'Remote Networks'
exact_networks = client.remote_networks.list(
   folder='Remote Networks',
   exact_match=True
)

for network in exact_networks:
   print(f"Exact match: {network.name} in {network.folder}")

# Exclude all remote networks from the 'All' folder
no_all_networks = client.remote_networks.list(
   folder='Remote Networks',
   exclude_folders=['All']
)

for network in no_all_networks:
   assert network.folder != 'All'
   print(f"Filtered out 'All': {network.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.remote_networks.list(
   folder='Remote Networks',
   exact_match=True,
   exclude_folders=['All'],
   regions=['us-east-1']
)

for network in combined_filters:
   print(f"Combined filters result: {network.name} in {network.folder}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

```python
from scm.client import ScmClient
from scm.config.deployment import RemoteNetworks

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom RemoteNetworks instance with max_limit
remote_networks_service = RemoteNetworks(client, max_limit=4321)
all_networks1 = remote_networks_service.list(folder='Remote Networks')

# Option 2: Use the unified client interface directly
# This will use the default max_limit (2500)
all_networks2 = client.remote_networks.list(folder='Remote Networks')

# Both options will auto-paginate through all available objects.
# The networks are fetched in chunks according to the max_limit.
```

### Deleting Remote Networks

```python
# Delete by ID
network_id = "123e4567-e89b-12d3-a456-426655440000"
client.remote_networks.delete(network_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Remote Networks"],
    "description": "Updated remote network configurations",
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
    # Create network configuration
    network_config = {
        "name": "test-network",
        "region": "us-east-1",
        "license_type": "FWAAS-AGGREGATE",
        "spn_name": "test-spn",
        "folder": "Remote Networks",
        "ecmp_load_balancing": "disable",
        "ipsec_tunnel": "test-tunnel",
        "subnets": ["10.0.0.0/24"]
    }

    # Create the network using the unified client interface
    new_network = client.remote_networks.create(network_config)

    # Commit changes directly from the client
    result = client.commit(
        folders=["Remote Networks"],
        description="Added test network",
        sync=True
    )

    # Check job status directly from the client
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid network data: {e.message}")
except NameNotUniqueError as e:
    print(f"Network name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Network not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Network still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.remote_networks`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Network Configuration**
    - Use descriptive names for networks and tunnels
    - Document subnet allocations
    - Consider ECMP for high availability
    - Validate BGP configurations
    - Use consistent naming conventions

3. **ECMP Management**
    - Plan tunnel configurations carefully
    - Balance traffic across tunnels
    - Monitor tunnel health
    - Configure appropriate timeouts
    - Document failover scenarios

4. **Container Management**
    - Always specify the correct folder container
    - Use consistent folder names across operations
    - Validate folder existence before operations

5. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

6. **Performance**
    - Use appropriate pagination for list operations
    - Cache frequently accessed networks
    - Implement proper retry mechanisms
    - Monitor timeout settings

## Full Script Examples

Refer to
the [remote_networks.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/deployment/remote_networks.py).

## Related Models

- [RemoteNetworkCreateModel](../../models/deployment/remote_networks_models.md#Overview)
- [RemoteNetworkUpdateModel](../../models/deployment/remote_networks_models.md#Overview)
- [RemoteNetworkResponseModel](../../models/deployment/remote_networks_models.md#Overview)
