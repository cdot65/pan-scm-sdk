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

| Method     | Description                           | Parameters                               | Return Type                       |
|------------|---------------------------------------|------------------------------------------|-----------------------------------|
| `create()` | Creates a new remote network          | `data: Dict[str, Any]`                   | `RemoteNetworkResponseModel`      |
| `get()`    | Retrieves a network by ID             | `object_id: str`                         | `RemoteNetworkResponseModel`      |
| `update()` | Updates an existing network           | `remote_network: RemoteNetworkUpdateModel`| `RemoteNetworkResponseModel`      |
| `delete()` | Deletes a network                     | `object_id: str`                         | `None`                            |
| `list()`   | Lists networks with filtering         | `folder: str`, `**filters`               | `List[RemoteNetworkResponseModel]`|
| `fetch()`  | Gets network by name and container    | `name: str`, `folder: str`               | `RemoteNetworkResponseModel`      |

## Remote Network Model Attributes

| Attribute            | Type           | Required | Description                                  |
|---------------------|----------------|----------|----------------------------------------------|
| `name`              | str            | Yes      | Name of network (max 63 chars)               |
| `id`                | UUID           | Yes*     | Unique identifier (*response only)           |
| `region`            | str            | Yes      | AWS region for deployment                    |
| `license_type`      | str            | Yes      | License type (default: FWAAS-AGGREGATE)      |
| `spn_name`          | str            | Yes**    | Service Provider Name (**required for FWAAS) |
| `description`       | str            | No       | Description (max 1023 chars)                 |
| `subnets`           | List[str]      | No       | List of network subnets                      |
| `ecmp_load_balancing`| str           | Yes      | ECMP mode (enable/disable)                   |
| `ecmp_tunnels`      | List[Dict]     | Yes***   | ECMP tunnel configs (***if ECMP enabled)     |
| `ipsec_tunnel`      | str            | Yes***   | IPSec tunnel name (***if ECMP disabled)      |
| `protocol`          | ProtocolModel  | No       | BGP protocol configuration                   |
| `folder`            | str            | Yes      | Folder location                              |

## Exceptions

| Exception                    | HTTP Code | Description                           |
|----------------------------|-----------|---------------------------------------|
| `InvalidObjectError`         | 400       | Invalid network data or format        |
| `MissingQueryParameterError` | 400       | Missing required parameters           |
| `NameNotUniqueError`         | 409       | Network name already exists           |
| `ObjectNotPresentError`      | 404       | Network not found                     |
| `ReferenceNotZeroError`      | 409       | Network still referenced              |
| `AuthenticationError`        | 401       | Authentication failed                 |
| `ServerError`                | 500       | Internal server error                 |

## Basic Configuration

<div class="termy">

<!-- termynal -->
```python
from scm.client import Scm
from scm.config.deployment import RemoteNetworks

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize RemoteNetworks object with custom max_limit
remote_networks = RemoteNetworks(client, max_limit=5000)
```

</div>

## Usage Examples

### Creating Remote Networks

<div class="termy">

<!-- termynal -->
```python
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
standard_network = remote_networks.create(standard_config)

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
ecmp_network = remote_networks.create(ecmp_config)
```

</div>

### Retrieving Remote Networks

<div class="termy">

<!-- termynal -->
```python
# Fetch by name and folder
network = remote_networks.fetch(
    name="branch-office-1", 
    folder="Remote Networks"
)
print(f"Found network: {network.name}")

# Get by ID
network_by_id = remote_networks.get(network.id)
print(f"Retrieved network: {network_by_id.name}")
print(f"Subnets: {', '.join(network_by_id.subnets)}")
```

</div>

### Updating Remote Networks

<div class="termy">

<!-- termynal -->
```python
# Fetch existing network
existing_network = remote_networks.fetch(
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
updated_network = remote_networks.update(existing_network)
```

</div>

### Listing Remote Networks

<div class="termy">

<!-- termynal -->
```python
# List with direct filter parameters
filtered_networks = remote_networks.list(
    folder='Remote Networks',
    regions=['us-east-1'],
    license_types=['FWAAS-AGGREGATE']
)

# Process results
for network in filtered_networks:
    print(f"Name: {network.name}")
    print(f"Region: {network.region}")
    print(f"Subnets: {', '.join(network.subnets)}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Remote Networks",
    "regions": ["us-west-2"],
    "spn_names": ["us-west-2-spn"]
}

# List with filters as kwargs
filtered_networks = remote_networks.list(**list_params)
```

</div>

### Deleting Remote Networks

<div class="termy">

<!-- termynal -->
```python
# Delete by ID
network_id = "123e4567-e89b-12d3-a456-426655440000"
remote_networks.delete(network_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->
```python
# Prepare commit parameters
commit_params = {
    "folders": ["Remote Networks"],
    "description": "Updated remote network configurations",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = remote_networks.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->
```python
# Get status of specific job
job_status = remote_networks.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = remote_networks.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->
```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
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

    # Create the network
    new_network = remote_networks.create(network_config)

    # Commit changes
    result = remote_networks.commit(
        folders=["Remote Networks"],
        description="Added test network",
        sync=True
    )

    # Check job status
    status = remote_networks.get_job_status(result.job_id)

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

</div>

## Best Practices

1. **Network Configuration**
    - Use descriptive names for networks and tunnels
    - Document subnet allocations
    - Consider ECMP for high availability
    - Validate BGP configurations
    - Use consistent naming conventions

2. **ECMP Management**
    - Plan tunnel configurations carefully
    - Balance traffic across tunnels
    - Monitor tunnel health
    - Configure appropriate timeouts
    - Document failover scenarios

3. **Performance**
    - Use appropriate max_limit settings
    - Implement pagination for large lists
    - Cache frequently accessed data
    - Monitor API rate limits
    - Use efficient filtering

4. **Security**
    - Follow least privilege principle
    - Validate input data
    - Secure tunnel configurations
    - Monitor authentication
    - Audit configuration changes

5. **Error Handling**
    - Implement comprehensive error handling
    - Log configuration changes
    - Monitor commit status
    - Track job completion
    - Document error patterns

## Full Script Examples

Refer to
the [remote_networks.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/deployment/remote_networks.py).

## Related Models

- [RemoteNetworkCreateModel](../../models/deployment/remote_networks_models.md#Overview)
- [RemoteNetworkUpdateModel](../../models/deployment/remote_networks_models.md#Overview)
- [RemoteNetworkResponseModel](../../models/deployment/remote_networks_models.md#Overview)
