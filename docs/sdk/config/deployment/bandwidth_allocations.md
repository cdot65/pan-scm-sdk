# Bandwidth Allocations

## Table of Contents

1. [Overview](#overview)
2. [Creating Bandwidth Allocations](#creating-bandwidth-allocations)
3. [Getting Bandwidth Allocations](#getting-bandwidth-allocations)
4. [Updating Bandwidth Allocations](#updating-bandwidth-allocations)
5. [Deleting Bandwidth Allocations](#deleting-bandwidth-allocations)
6. [QoS Settings](#qos-settings)
7. [Code Examples](#code-examples)
8. [API Reference](#api-reference)

## Overview

The `BandwidthAllocations` class provides functionality for managing bandwidth allocations in Strata Cloud Manager. Bandwidth allocations allow you to define and control how bandwidth is distributed across service provider networks (SPNs) within specific regions.

These bandwidth allocation configurations can include Quality of Service (QoS) settings to prioritize certain types of traffic and ensure critical applications receive adequate network resources.

## Creating Bandwidth Allocations

To create a new bandwidth allocation, you need to provide:

- **name**: A descriptive name for the bandwidth allocation region
- **allocated_bandwidth**: The amount of bandwidth allocated in Mbps
- **spn_name_list**: A list of service provider network names that will share this allocation
- **qos** (Optional): Quality of Service settings

### Example

```python
from scm.client import Scm

# Initialize the client
client = Scm(
    client_id="your_client_id", 
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create a new bandwidth allocation
result = client.bandwidth_allocation.create({
    "name": "us-east-allocation",
    "allocated_bandwidth": 200,
    "spn_name_list": ["us-east-spn1", "us-east-spn2"],
    "qos": {
        "enabled": True,
        "customized": True,
        "profile": "business-critical",
        "guaranteed_ratio": 0.6
    }
})

print(f"Created bandwidth allocation: {result.name}")
```

## Getting Bandwidth Allocations

### Listing All Bandwidth Allocations

You can retrieve all bandwidth allocations:

```python
# List all bandwidth allocations
allocations = client.bandwidth_allocation.list()

for allocation in allocations:
    print(f"Allocation: {allocation.name}, Bandwidth: {allocation.allocated_bandwidth} Mbps")
    print(f"SPN List: {allocation.spn_name_list}")
    if allocation.qos:
        print(f"QoS Enabled: {allocation.qos.enabled}")
```

### Filtering Bandwidth Allocations

The `list()` method supports several filters:

- **name**: Filter by region name
- **allocated_bandwidth**: Filter by allocated bandwidth amount
- **spn_name_list**: Filter by specific SPN names
- **qos_enabled**: Filter by QoS enabled status

```python
# Get allocations with QoS enabled
qos_allocations = client.bandwidth_allocation.list(qos_enabled=True)

# Get allocations for specific SPNs
spn_allocations = client.bandwidth_allocation.list(spn_name_list="us-east-spn1")

# Get allocations with a specific bandwidth
high_bw_allocations = client.bandwidth_allocation.list(allocated_bandwidth=500)
```

### Getting a Specific Bandwidth Allocation

You can fetch a specific bandwidth allocation by name:

```python
# Get a specific bandwidth allocation by name
allocation = client.bandwidth_allocation.get(name="us-east-allocation")

if allocation:
    print(f"Found allocation: {allocation.name}")
else:
    print("Allocation not found")
```

The `fetch()` method works similarly but raises an exception if the allocation is not found:

```python
try:
    allocation = client.bandwidth_allocation.fetch(name="us-east-allocation")
    print(f"Found allocation: {allocation.name}")
except Exception as e:
    print(f"Error fetching allocation: {e}")
```

## Updating Bandwidth Allocations

You can update an existing bandwidth allocation:

```python
# Update a bandwidth allocation
updated_allocation = client.bandwidth_allocation.update({
    "name": "us-east-allocation",
    "allocated_bandwidth": 300,  # Increase bandwidth
    "spn_name_list": ["us-east-spn1", "us-east-spn2", "us-east-spn3"],  # Add a new SPN
    "qos": {
        "enabled": True,
        "customized": False,
        "profile": "standard",
        "guaranteed_ratio": 0.5
    }
})

print(f"Updated allocation: {updated_allocation.name}")
print(f"New bandwidth: {updated_allocation.allocated_bandwidth} Mbps")
print(f"New SPN list: {updated_allocation.spn_name_list}")
```

## Deleting Bandwidth Allocations

To delete a bandwidth allocation, you must provide both the name and the SPNs as a comma-separated string:

```python
# Delete a bandwidth allocation
client.bandwidth_allocation.delete(
    name="us-east-allocation",
    spn_name_list="us-east-spn1,us-east-spn2,us-east-spn3"
)

print("Bandwidth allocation deleted")
```

## QoS Settings

Quality of Service (QoS) settings allow you to prioritize network traffic:

- **enabled**: Whether QoS is enabled for this allocation (boolean)
- **customized**: Whether custom QoS settings are used (boolean)
- **profile**: The QoS profile name to apply (string)
- **guaranteed_ratio**: The ratio of bandwidth guaranteed for prioritized traffic (float between 0 and 1)

Example of configuring QoS settings:

```python
# Create a bandwidth allocation with QoS settings
allocation = client.bandwidth_allocation.create({
    "name": "qos-allocation",
    "allocated_bandwidth": 500,
    "spn_name_list": ["spn1", "spn2"],
    "qos": {
        "enabled": True,
        "customized": True,
        "profile": "high-priority",
        "guaranteed_ratio": 0.7  # 70% of bandwidth guaranteed for high-priority traffic
    }
})
```

## Code Examples

### Complete Example with Error Handling

```python
from scm.client import Scm
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

# Initialize the client
client = Scm(
    client_id="your_client_id", 
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Create a new bandwidth allocation
    new_allocation = client.bandwidth_allocation.create({
        "name": "test-region",
        "allocated_bandwidth": 100,
        "spn_name_list": ["spn1", "spn2"],
        "qos": {
            "enabled": True,
            "customized": True,
            "profile": "test-profile",
            "guaranteed_ratio": 0.5
        }
    })
    
    print(f"Created allocation: {new_allocation.name}")
    
    # List all allocations
    all_allocations = client.bandwidth_allocation.list()
    print(f"Total allocations: {len(all_allocations)}")
    
    # Update the allocation
    updated_allocation = client.bandwidth_allocation.update({
        "name": "test-region",
        "allocated_bandwidth": 200,  # Increased bandwidth
        "spn_name_list": ["spn1", "spn2"]
    })
    
    print(f"Updated allocation bandwidth: {updated_allocation.allocated_bandwidth} Mbps")
    
    # Delete the allocation when finished
    client.bandwidth_allocation.delete(
        name="test-region",
        spn_name_list="spn1,spn2"
    )
    
    print("Allocation deleted successfully")
    
except InvalidObjectError as e:
    print(f"Invalid object error: {e}")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## API Reference

### BandwidthAllocations Class

```python
class BandwidthAllocations(BaseObject):
    """
    Manages Bandwidth Allocation objects in Palo Alto Networks' Strata Cloud Manager.
    
    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 200. Must be between 1 and 1000.
    """
```

### Methods

| Method                        | Description                                         | Required Parameters                          | Optional Parameters                                   |
|-------------------------------|-----------------------------------------------------|----------------------------------------------|-------------------------------------------------------|
| `create(data)`                | Creates a new bandwidth allocation                  | name, allocated_bandwidth, spn_name_list     | qos                                                   |
| `update(data)`                | Updates an existing bandwidth allocation            | name                                         | allocated_bandwidth, spn_name_list, qos               |
| `list()`                      | Lists bandwidth allocations with optional filtering | None                                         | name, allocated_bandwidth, spn_name_list, qos_enabled |
| `get(name)`                   | Gets a specific bandwidth allocation                | name                                         | None                                                  |
| `fetch(name)`                 | Fetches a specific bandwidth allocation             | name                                         | None                                                  |
| `delete(name, spn_name_list)` | Deletes a bandwidth allocation                      | name, spn_name_list (comma-separated string) | None                                                  |

For more information about the data models used by these methods, see the [Bandwidth Allocation Models](../../models/deployment/bandwidth_allocation_models.md) documentation.
