# Bandwidth Allocations Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Bandwidth Allocation Model Attributes](#bandwidth-allocation-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Bandwidth Allocations](#creating-bandwidth-allocations)
    - [Retrieving Bandwidth Allocations](#retrieving-bandwidth-allocations)
    - [Updating Bandwidth Allocations](#updating-bandwidth-allocations)
    - [Listing Bandwidth Allocations](#listing-bandwidth-allocations)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Bandwidth Allocations](#deleting-bandwidth-allocations)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `BandwidthAllocations` class provides functionality to manage bandwidth allocations in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting bandwidth allocation configurations that control how bandwidth is distributed across service provider networks (SPNs) within specific regions.

## Core Methods

| Method     | Description                        | Parameters                                 | Return Type                           |
|------------|------------------------------------|--------------------------------------------|-----------------------------------------|
| `create()` | Creates a new bandwidth allocation | `data: Dict[str, Any]`                     | `BandwidthAllocationResponseModel`       |
| `get()`    | Retrieves an allocation by name    | `name: str`                                | `BandwidthAllocationResponseModel`       |
| `update()` | Updates an existing allocation     | `data: Dict[str, Any]`                     | `BandwidthAllocationResponseModel`       |
| `delete()` | Deletes an allocation              | `name: str`, `spn_name_list: str`          | `None`                                   |
| `list()`   | Lists allocations with filtering   | `**filters`                                | `List[BandwidthAllocationResponseModel]` |
| `fetch()`  | Gets allocation by name            | `name: str`                                | `BandwidthAllocationResponseModel`       |

## Bandwidth Allocation Model Attributes

| Attribute              | Type          | Required | Description                                   |
|------------------------|---------------|----------|----------------------------------------------|
| `name`                 | str           | Yes      | Name of the bandwidth allocation region       |
| `allocated_bandwidth`  | int           | Yes      | Bandwidth amount in Mbps                     |
| `spn_name_list`        | List[str]     | Yes      | List of service provider network names       |
| `qos`                  | QoSModel      | No       | Quality of Service settings                   |

### QoS Model Attributes

| Attribute            | Type  | Required | Description                                          |
|----------------------|-------|----------|------------------------------------------------------|
| `enabled`            | bool  | Yes      | Whether QoS is enabled                               |
| `customized`         | bool  | No       | Whether custom QoS settings are used                 |
| `profile`            | str   | No       | QoS profile name                                     |
| `guaranteed_ratio`   | float | No       | Ratio of bandwidth guaranteed (0.0 to 1.0)           |

## Exceptions

| Exception                    | HTTP Code | Description                          |
|------------------------------|-----------|--------------------------------------|
| `InvalidObjectError`         | 400       | Invalid allocation data or format    |
| `MissingQueryParameterError` | 400       | Missing required parameters          |
| `NameNotUniqueError`         | 409       | Allocation name already exists       |
| `ObjectNotPresentError`      | 404       | Allocation not found                 |
| `AuthenticationError`        | 401       | Authentication failed                |
| `ServerError`                | 500       | Internal server error                |

## Basic Configuration

The Bandwidth Allocations service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

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

# Access the Bandwidth Allocations service directly through the client
# No need to create a separate BandwidthAllocations instance
allocations = client.bandwidth_allocation
```

</div>

### Traditional Service Instantiation (Legacy)

<div class="termy">

<!-- termynal -->
```python
from scm.client import Scm
from scm.config.deployment import BandwidthAllocations

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize BandwidthAllocations object explicitly
allocations = BandwidthAllocations(client)
```

</div>

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Bandwidth Allocations

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

# Standard bandwidth allocation without QoS
standard_config = {
    "name": "standard-allocation",
    "allocated_bandwidth": 100,
    "spn_name_list": ["east-spn1", "east-spn2"]
}

# Create standard allocation
standard_allocation = client.bandwidth_allocation.create(standard_config)
print(f"Created allocation: {standard_allocation.name}")
print(f"Allocated bandwidth: {standard_allocation.allocated_bandwidth} Mbps")

# QoS-enabled bandwidth allocation
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

# Create QoS-enabled allocation
qos_allocation = client.bandwidth_allocation.create(qos_config)
print(f"Created QoS allocation: {qos_allocation.name}")
print(f"QoS enabled: {qos_allocation.qos.enabled}")
print(f"QoS guaranteed ratio: {qos_allocation.qos.guaranteed_ratio}")
```

</div>

### Retrieving Bandwidth Allocations

<div class="termy">

<!-- termynal -->
```python
# Get by name
allocation = client.bandwidth_allocation.get(name="standard-allocation")
print(f"Found allocation: {allocation.name}")
print(f"SPNs: {allocation.spn_name_list}")

# Fetch by name (raises exception if not found)
try:
    allocation = client.bandwidth_allocation.fetch(name="qos-allocation")
    print(f"Fetched allocation: {allocation.name}")
    if allocation.qos:
        print(f"QoS profile: {allocation.qos.profile}")
except Exception as e:
    print(f"Error: {e}")
```

</div>

### Updating Bandwidth Allocations

<div class="termy">

<!-- termynal -->
```python
# Update bandwidth allocation
update_config = {
    "name": "standard-allocation",
    "allocated_bandwidth": 200,  # Increase bandwidth
    "spn_name_list": ["east-spn1", "east-spn2", "east-spn3"],  # Add a new SPN
    "qos": {  # Add QoS settings
        "enabled": True,
        "customized": False,
        "profile": "standard",
        "guaranteed_ratio": 0.5
    }
}

# Perform update
updated_allocation = client.bandwidth_allocation.update(update_config)
print(f"Updated allocation: {updated_allocation.name}")
print(f"New bandwidth: {updated_allocation.allocated_bandwidth} Mbps")
print(f"New SPN list: {updated_allocation.spn_name_list}")
print(f"QoS now enabled: {updated_allocation.qos.enabled}")
```

</div>

### Listing Bandwidth Allocations

<div class="termy">

<!-- termynal -->
```python
# List all bandwidth allocations
all_allocations = client.bandwidth_allocation.list()
print(f"Total allocations: {len(all_allocations)}")

# Process results
for allocation in all_allocations:
    print(f"Name: {allocation.name}")
    print(f"Bandwidth: {allocation.allocated_bandwidth} Mbps")
    print(f"SPNs: {allocation.spn_name_list}")
    if allocation.qos and allocation.qos.enabled:
        print(f"QoS profile: {allocation.qos.profile}")

# List with filters
qos_enabled_allocations = client.bandwidth_allocation.list(qos_enabled=True)
print(f"Allocations with QoS enabled: {len(qos_enabled_allocations)}")

# List allocations for specific SPNs
spn_allocations = client.bandwidth_allocation.list(spn_name_list="east-spn1")
print(f"Allocations with east-spn1: {len(spn_allocations)}")

# List allocations with specific bandwidth
high_bandwidth_allocations = client.bandwidth_allocation.list(allocated_bandwidth=500)
print(f"Allocations with 500 Mbps: {len(high_bandwidth_allocations)}")
```

</div>

### Filtering Responses

The `list()` method supports several filters to refine your query results:

**Parameters:**

- `name`: Filter by region name
- `allocated_bandwidth`: Filter by allocated bandwidth amount
- `spn_name_list`: Filter by specific SPN names
- `qos_enabled`: Filter by QoS enabled status

**Examples:**

<div class="termy">

<!-- termynal -->
```python
# Get allocations with QoS enabled
qos_allocations = client.bandwidth_allocation.list(qos_enabled=True)
print(f"Allocations with QoS enabled: {len(qos_allocations)}")

# Get allocations for specific SPNs
spn_allocations = client.bandwidth_allocation.list(spn_name_list="east-spn1")
print(f"Allocations with east-spn1: {len(spn_allocations)}")

# Get allocations with a specific bandwidth
high_bw_allocations = client.bandwidth_allocation.list(allocated_bandwidth=500)
print(f"Allocations with 500 Mbps: {len(high_bw_allocations)}")

# Combine multiple filters
combined_filters = client.bandwidth_allocation.list(
    qos_enabled=True,
    allocated_bandwidth=500
)
print(f"Allocations with QoS and 500 Mbps: {len(combined_filters)}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 200. If you have a large number of bandwidth allocations, adjusting `max_limit` can help manage retrieval performance and memory usage.

**Example:**

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient
from scm.config.deployment import BandwidthAllocations

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom BandwidthAllocations instance with max_limit
bandwidth_allocation_service = BandwidthAllocations(client, max_limit=500)
all_allocations1 = bandwidth_allocation_service.list()

# Option 2: Use the unified client interface directly
# This will use the default max_limit (200)
all_allocations2 = client.bandwidth_allocation.list()

# Both options will auto-paginate through all available objects.
# The allocations are fetched in chunks according to the max_limit.
```

</div>

### Deleting Bandwidth Allocations

<div class="termy">

<!-- termynal -->
```python
# Delete a bandwidth allocation
# Note: For deleting, you must provide both the name and the SPNs as a comma-separated string
client.bandwidth_allocation.delete(
    name="standard-allocation",
    spn_name_list="east-spn1,east-spn2,east-spn3"
)
print("Bandwidth allocation deleted")
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->
```python
# Prepare commit parameters
commit_params = {
    "description": "Updated bandwidth allocations",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
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
    # Create bandwidth allocation configuration
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

    # Create the bandwidth allocation using the unified client interface
    new_allocation = client.bandwidth_allocation.create(allocation_config)
    print(f"Created allocation: {new_allocation.name}")

    # Commit changes directly from the client
    result = client.commit(
        description="Added test allocation",
        sync=True
    )

    # Check job status directly from the client
    status = client.get_job_status(result.job_id)
    print(f"Job status: {status.data[0].status_str}")

except InvalidObjectError as e:
    print(f"Invalid allocation data: {e.message}")
except NameNotUniqueError as e:
    print(f"Allocation name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Allocation not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.bandwidth_allocation`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Bandwidth Planning**
    - Allocate appropriate bandwidth for your SPNs
    - Consider traffic patterns and peak requirements
    - Document bandwidth allocation rationale
    - Review allocations regularly
    - Plan for future growth

3. **QoS Configuration**
    - Use QoS for applications with critical traffic requirements
    - Set appropriate guaranteed ratios
    - Document QoS profile choices
    - Test QoS settings before production deployment
    - Monitor QoS effectiveness

4. **SPN Management**
    - Verify SPN existence before creating allocations
    - Use consistent naming conventions
    - Group related SPNs in the same allocation
    - Document SPN relationships
    - Review and update SPN memberships regularly

5. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Validate input data before operations
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting
    - Monitor allocation changes

6. **Performance**
    - Use appropriate pagination for list operations
    - Implement proper retry mechanisms
    - Monitor timeout settings
    - Consider bandwidth allocation impacts on overall network performance

## Full Script Examples

Refer to
the [bandwidth_allocations.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/deployment/bandwidth_allocations.py).

## Related Models

- [BandwidthAllocationCreateModel](../../models/deployment/bandwidth_allocation_models.md#Overview)
- [BandwidthAllocationUpdateModel](../../models/deployment/bandwidth_allocation_models.md#Overview)
- [BandwidthAllocationResponseModel](../../models/deployment/bandwidth_allocation_models.md#Overview)
- [QoSModel](../../models/deployment/bandwidth_allocation_models.md#Overview)
