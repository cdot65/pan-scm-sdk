# Remote Networks Configuration Object

Manages remote network configurations with support for standard and ECMP-enabled setups in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `RemoteNetworks` class inherits from `BaseObject` and provides CRUD operations for remote network configurations.

### Methods

| Method     | Description                        | Parameters                                 | Return Type                        |
|------------|------------------------------------|--------------------------------------------|------------------------------------|
| `create()` | Creates a new remote network       | `data: Dict[str, Any]`                     | `RemoteNetworkResponseModel`       |
| `get()`    | Retrieves a network by ID          | `object_id: str`                           | `RemoteNetworkResponseModel`       |
| `update()` | Updates an existing network        | `remote_network: RemoteNetworkUpdateModel` | `RemoteNetworkResponseModel`       |
| `delete()` | Deletes a network                  | `object_id: str`                           | `None`                             |
| `list()`   | Lists networks with filtering      | `folder: str`, `**filters`                 | `List[RemoteNetworkResponseModel]` |
| `fetch()`  | Gets network by name and container | `name: str`, `folder: str`                 | `RemoteNetworkResponseModel`       |

### Model Attributes

| Attribute                | Type                  | Required | Default         | Description                                  |
|--------------------------|-----------------------|----------|-----------------|----------------------------------------------|
| `name`                   | str                   | Yes      | None            | Name of network (max 63 chars)               |
| `id`                     | UUID                  | Yes*     | None            | Unique identifier (*response only)           |
| `region`                 | str                   | Yes      | None            | Region for deployment                        |
| `license_type`           | str                   | No       | FWAAS-AGGREGATE | License type                                 |
| `spn_name`               | str                   | Yes**    | None            | Service Provider Name (**required for FWAAS) |
| `description`            | str                   | No       | None            | Description (max 1023 chars)                 |
| `subnets`                | List[str]             | No       | None            | List of network subnets                      |
| `ecmp_load_balancing`    | EcmpLoadBalancingEnum | No       | disable         | ECMP mode (enable/disable)                   |
| `ecmp_tunnels`           | List[EcmpTunnelModel] | Yes***   | None            | ECMP tunnel configs (***if ECMP enabled)     |
| `ipsec_tunnel`           | str                   | Yes***   | None            | IPSec tunnel name (***if ECMP disabled)      |
| `secondary_ipsec_tunnel` | str                   | No       | None            | Secondary IPSec tunnel name                  |
| `protocol`               | ProtocolModel         | No       | None            | BGP protocol configuration                   |
| `folder`                 | str                   | No****   | None            | Folder location (max 64 chars)               |
| `snippet`                | str                   | No****   | None            | Snippet location (max 64 chars)              |
| `device`                 | str                   | No****   | None            | Device location (max 64 chars)               |

\* Only required for response models
\** Required when license_type is FWAAS-AGGREGATE
\*** Mutually exclusive: `ecmp_tunnels` when ECMP enabled, `ipsec_tunnel` when disabled
\**** Exactly one container (`folder`, `snippet`, or `device`) must be provided for create operations

### Exceptions

| Exception                    | HTTP Code | Description                    |
|------------------------------|-----------|--------------------------------|
| `InvalidObjectError`         | 400       | Invalid network data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters    |
| `NameNotUniqueError`         | 409       | Network name already exists    |
| `ObjectNotPresentError`      | 404       | Network not found              |
| `ReferenceNotZeroError`      | 409       | Network still referenced       |
| `AuthenticationError`        | 401       | Authentication failed          |
| `ServerError`                | 500       | Internal server error          |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

networks = client.remote_network
```

## Methods

### List Remote Networks

```python
filtered_networks = client.remote_network.list(
    folder='Remote Networks',
    regions=['us-east-1']
)

for network in filtered_networks:
    print(f"Name: {network.name}")
    print(f"Region: {network.region}")
```

**Filtering responses:**

```python
exact_networks = client.remote_network.list(
    folder='Remote Networks',
    exact_match=True
)

combined_filters = client.remote_network.list(
    folder='Remote Networks',
    exact_match=True,
    exclude_folders=['All'],
    regions=['us-east-1']
)
```

**Controlling pagination with max_limit:**

```python
client.remote_network.max_limit = 4000

all_networks = client.remote_network.list(folder='Remote Networks')
```

### Fetch a Remote Network

```python
network = client.remote_network.fetch(
    name="branch-office-1",
    folder="Remote Networks"
)
print(f"Found network: {network.name}")
```

### Create a Remote Network

```python
# Standard remote network
standard_config = {
    "name": "branch-office-1",
    "region": "us-east-1",
    "license_type": "FWAAS-AGGREGATE",
    "spn_name": "us-east-1-spn",
    "folder": "Remote Networks",
    "subnets": ["10.0.0.0/24", "10.0.1.0/24"],
    "ecmp_load_balancing": "disable",
    "ipsec_tunnel": "branch-1-tunnel"
}
standard_network = client.remote_network.create(standard_config)

# ECMP-enabled remote network
ecmp_config = {
    "name": "branch-office-2",
    "region": "us-west-2",
    "license_type": "FWAAS-AGGREGATE",
    "spn_name": "us-west-2-spn",
    "folder": "Remote Networks",
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
ecmp_network = client.remote_network.create(ecmp_config)
```

### Update a Remote Network

```python
existing_network = client.remote_network.fetch(
    name="branch-office-1",
    folder="Remote Networks"
)

existing_network.description = "Updated branch office configuration"
existing_network.subnets = ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]
existing_network.protocol = {
    "bgp": {
        "enable": True,
        "peer_as": "65515",
        "peer_ip_address": "10.0.0.1",
        "local_ip_address": "10.0.0.2"
    }
}

updated_network = client.remote_network.update(existing_network)
```

### Delete a Remote Network

```python
client.remote_network.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get a Remote Network by ID

```python
network_by_id = client.remote_network.get(network.id)
print(f"Retrieved network: {network_by_id.name}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Remote Networks"],
    description="Updated remote network configurations",
    sync=True,
    timeout=300
)
print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

try:
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
    new_network = client.remote_network.create(network_config)
    result = client.commit(
        folders=["Remote Networks"],
        description="Added test network",
        sync=True
    )
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

## Related Topics

- [Remote Network Models](../../models/deployment/remote_networks_models.md#Overview)
- [Deployment Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/deployment/remote_networks.py)
