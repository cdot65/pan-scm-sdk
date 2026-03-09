# Bandwidth Allocations Configuration Object

Manages bandwidth allocation objects for distributing bandwidth across service provider networks in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `BandwidthAllocations` class inherits from `BaseObject` and provides CRUD operations for bandwidth allocation configurations that control how bandwidth is distributed across service provider networks (SPNs) within specific regions.

### Methods

| Method     | Description                        | Parameters                        | Return Type                              |
|------------|------------------------------------|-----------------------------------|------------------------------------------|
| `create()` | Creates a new bandwidth allocation | `data: Dict[str, Any]`            | `BandwidthAllocationResponseModel`       |
| `get()`    | Retrieves an allocation by name    | `name: str`                       | `BandwidthAllocationResponseModel`       |
| `update()` | Updates an existing allocation     | `data: Dict[str, Any]`            | `BandwidthAllocationResponseModel`       |
| `delete()` | Deletes an allocation              | `name: str`, `spn_name_list: str` | `None`                                   |
| `list()`   | Lists allocations with filtering   | `**filters`                       | `List[BandwidthAllocationResponseModel]` |
| `fetch()`  | Gets allocation by name            | `name: str`                       | `BandwidthAllocationResponseModel`       |

### Model Attributes

| Attribute             | Type      | Required | Default | Description                                        |
|-----------------------|-----------|----------|---------|----------------------------------------------------|
| `name`                | str       | Yes      | None    | Name of the bandwidth allocation region (max 63 chars) |
| `allocated_bandwidth` | float     | Yes      | None    | Bandwidth amount in Mbps (must be > 0)             |
| `spn_name_list`       | List[str] | No       | None    | List of service provider network names             |
| `qos`                 | QosModel  | No       | None    | Quality of Service settings                        |

#### QoS Model Attributes

| Attribute          | Type  | Required | Default | Description                    |
|--------------------|-------|----------|---------|--------------------------------|
| `enabled`          | bool  | No       | None    | Whether QoS is enabled         |
| `customized`       | bool  | No       | None    | Whether custom QoS settings are used |
| `profile`          | str   | No       | None    | QoS profile name               |
| `guaranteed_ratio` | float | No       | None    | Ratio of bandwidth guaranteed  |

### Exceptions

| Exception                    | HTTP Code | Description                       |
|------------------------------|-----------|-----------------------------------|
| `InvalidObjectError`         | 400       | Invalid allocation data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters       |
| `NameNotUniqueError`         | 409       | Allocation name already exists    |
| `ObjectNotPresentError`      | 404       | Allocation not found              |
| `AuthenticationError`        | 401       | Authentication failed             |
| `ServerError`                | 500       | Internal server error             |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

allocations = client.bandwidth_allocation
```

## Methods

### List Bandwidth Allocations

```python
all_allocations = client.bandwidth_allocation.list()

for allocation in all_allocations:
    print(f"Name: {allocation.name}")
    print(f"Bandwidth: {allocation.allocated_bandwidth} Mbps")
    print(f"SPNs: {allocation.spn_name_list}")
    if allocation.qos and allocation.qos.enabled:
        print(f"QoS profile: {allocation.qos.profile}")
```

**Filtering responses:**

```python
# Filter by QoS enabled status
qos_allocations = client.bandwidth_allocation.list(qos_enabled=True)

# Filter by specific SPN
spn_allocations = client.bandwidth_allocation.list(spn_name_list="east-spn1")

# Filter by bandwidth amount
high_bw_allocations = client.bandwidth_allocation.list(allocated_bandwidth=500)

# Combine multiple filters
combined_filters = client.bandwidth_allocation.list(
    qos_enabled=True,
    allocated_bandwidth=500
)
```

**Controlling pagination with max_limit:**

```python
client.bandwidth_allocation.max_limit = 500

all_allocations = client.bandwidth_allocation.list()
```

### Fetch a Bandwidth Allocation

```python
allocation = client.bandwidth_allocation.fetch(name="qos-allocation")
print(f"Fetched allocation: {allocation.name}")
if allocation.qos:
    print(f"QoS profile: {allocation.qos.profile}")
```

### Create a Bandwidth Allocation

```python
# Standard allocation without QoS
standard_config = {
    "name": "standard-allocation",
    "allocated_bandwidth": 100,
    "spn_name_list": ["east-spn1", "east-spn2"]
}
standard_allocation = client.bandwidth_allocation.create(standard_config)

# QoS-enabled allocation
qos_config = {
    "name": "qos-allocation",
    "allocated_bandwidth": 500,
    "spn_name_list": ["west-spn1", "west-spn2"],
    "qos": {
        "enabled": True,
        "customized": True,
        "profile": "high-priority",
        "guaranteed_ratio": 0.7
    }
}
qos_allocation = client.bandwidth_allocation.create(qos_config)
```

### Update a Bandwidth Allocation

```python
update_config = {
    "name": "standard-allocation",
    "allocated_bandwidth": 200,
    "spn_name_list": ["east-spn1", "east-spn2", "east-spn3"],
    "qos": {
        "enabled": True,
        "customized": False,
        "profile": "standard",
        "guaranteed_ratio": 0.5
    }
}
updated_allocation = client.bandwidth_allocation.update(update_config)
```

### Delete a Bandwidth Allocation

```python
# Delete requires both name and SPNs as a comma-separated string
client.bandwidth_allocation.delete(
    name="standard-allocation",
    spn_name_list="east-spn1,east-spn2,east-spn3"
)
```

### Get a Bandwidth Allocation by Name

```python
allocation = client.bandwidth_allocation.get(name="standard-allocation")
print(f"Found allocation: {allocation.name}")
print(f"SPNs: {allocation.spn_name_list}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    description="Updated bandwidth allocations",
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
    ObjectNotPresentError
)

try:
    allocation_config = {
        "name": "test-allocation",
        "allocated_bandwidth": 100,
        "spn_name_list": ["test-spn1", "test-spn2"],
        "qos": {
            "enabled": True,
            "profile": "standard",
            "guaranteed_ratio": 0.5
        }
    }
    new_allocation = client.bandwidth_allocation.create(allocation_config)
    result = client.commit(
        description="Added test allocation",
        sync=True
    )
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid allocation data: {e.message}")
except NameNotUniqueError as e:
    print(f"Allocation name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Allocation not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Bandwidth Allocation Models](../../models/deployment/bandwidth_allocation_models.md#Overview)
- [Deployment Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/deployment/bandwidth_allocations.py)
