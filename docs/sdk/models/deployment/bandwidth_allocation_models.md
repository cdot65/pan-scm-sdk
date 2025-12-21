# Bandwidth Allocation Models

## Overview {#Overview}

The Bandwidth Allocation models provide a structured way to manage bandwidth allocation configurations in Palo Alto Networks' Strata Cloud Manager. These models allow you to create, update, and manage bandwidth allocations for different regions, supporting optional Quality of Service (QoS) configurations.

### Models

The module provides the following Pydantic models:

- `BandwidthAllocationBaseModel`: Base model with fields common to all bandwidth allocation operations
- `BandwidthAllocationCreateModel`: Model for creating new bandwidth allocations
- `BandwidthAllocationUpdateModel`: Model for updating existing bandwidth allocations
- `BandwidthAllocationResponseModel`: Response model for bandwidth allocation operations
- `BandwidthAllocationListResponseModel`: Response model for list operations (includes pagination)
- `QosModel`: Model for Quality of Service configuration

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute           | Type          | Required | Default | Description                                                     |
|---------------------|---------------|----------|---------|------------------------------------------------------------------|
| name                | str           | Yes      | None    | Name of the aggregated bandwidth region. Must match pattern `^[0-9a-zA-Z._\- ]+$` |
| allocated_bandwidth | float         | Yes      | None    | Bandwidth to allocate in Mbps, must be greater than 0           |
| spn_name_list       | List[str]     | No       | None    | List of SPN (Service Processing Node) names for this region      |
| qos                 | QosModel      | No       | None    | Quality of Service configuration for bandwidth allocation        |

### QoS Model Attributes

| Attribute        | Type     | Required | Default | Description                             |
|------------------|----------|----------|---------|-----------------------------------------|
| enabled          | bool     | No       | None    | Enable QoS for bandwidth allocation     |
| customized       | bool     | No       | None    | Use customized QoS settings             |
| profile          | str      | No       | None    | QoS profile name                        |
| guaranteed_ratio | float    | No       | None    | Guaranteed ratio for bandwidth          |

## Model Validators

The Bandwidth Allocation models enforce data validation through Pydantic:

- The `name` field must match the pattern `^[0-9a-zA-Z._\- ]+$` and be at most 63 characters long
- The `allocated_bandwidth` must be a positive number (greater than 0)
- Quality of Service (QoS) settings are optional but must follow the QosModel structure when provided

## Usage Examples

### Creating a Bandwidth Allocation

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
allocation_dict = {
    "name": "west-region",
    "allocated_bandwidth": 100,
    "spn_name_list": ["spn1", "spn2"]
}

response = client.bandwidth_allocation.create(allocation_dict)
print(f"Created allocation: {response.name} with {response.allocated_bandwidth} Mbps")
```

### Creating a Bandwidth Allocation with QoS

```python
# Using dictionary with QoS configuration
qos_dict = {
    "name": "east-region",
    "allocated_bandwidth": 200,
    "spn_name_list": ["spn3", "spn4"],
    "qos": {
        "enabled": True,
        "customized": True,
        "profile": "high-priority",
        "guaranteed_ratio": 0.7
    }
}

response = client.bandwidth_allocation.create(qos_dict)
print(f"Created QoS allocation: {response.name}")
if response.qos:
    print(f"QoS profile: {response.qos.profile}")
```

### Updating a Bandwidth Allocation

```python
# Fetch existing allocation
existing = client.bandwidth_allocation.fetch(name="west-region")

# Modify attributes using dot notation
existing.allocated_bandwidth = 150
existing.spn_name_list = ["spn1", "spn2", "spn5"]

# Pass modified object to update() as dictionary
updated = client.bandwidth_allocation.update(existing.model_dump())
print(f"Updated allocation: {updated.name} to {updated.allocated_bandwidth} Mbps")
```

### List Bandwidth Allocations

```python
# List all bandwidth allocations
all_allocations = client.bandwidth_allocation.list()

# Filter by name
filtered_allocations = client.bandwidth_allocation.list(name="west-region")

# Filter by allocated bandwidth
high_bandwidth = client.bandwidth_allocation.list(allocated_bandwidth=200)

# Filter by SPN name
allocations_with_spn = client.bandwidth_allocation.list(spn_name_list="spn1")

# Filter by QoS enabled status
qos_enabled_allocations = client.bandwidth_allocation.list(qos_enabled=True)
```

### Get a Single Bandwidth Allocation

```python
# Get a bandwidth allocation by name (returns None if not found)
allocation = client.bandwidth_allocation.get("west-region")
if allocation:
    print(f"Found: {allocation.name}")

# Fetch will raise an exception if not found
try:
    allocation = client.bandwidth_allocation.fetch("west-region")
    print(f"Fetched: {allocation.name}")
except InvalidObjectError:
    print("Bandwidth allocation not found")
```

### Delete a Bandwidth Allocation

```python
# Delete a bandwidth allocation by name and SPN name list (comma-separated)
client.bandwidth_allocation.delete("west-region", "spn1,spn2")
print("Bandwidth allocation deleted")
```

## List Response Format

When listing bandwidth allocations, the API returns a paginated response with the following structure:

```python
{
    "data": [
        {
            "name": "west-region",
            "allocated_bandwidth": 100,
            "spn_name_list": ["spn1", "spn2"],
            "qos": {
                "enabled": true,
                "customized": true,
                "profile": "high-priority",
                "guaranteed_ratio": 0.7
            }
        },
        {
            "name": "east-region",
            "allocated_bandwidth": 200,
            "spn_name_list": ["spn3", "spn4"]
        }
    ],
    "limit": 200,
    "offset": 0,
    "total": 2
}
```

## Best Practices

1. **Naming Conventions**
   - Use consistent naming patterns for all bandwidth allocations
   - Consider including region information in the name for clarity

2. **Bandwidth Allocation**
   - Allocate bandwidth conservatively based on actual usage needs
   - Monitor allocation usage to adjust as needed

3. **Quality of Service (QoS)**
   - Use QoS configurations for critical applications that require bandwidth guarantees
   - Set reasonable guaranteed ratios that won't starve other traffic

4. **SPN Configuration**
   - Maintain a clear inventory of which SPNs are assigned to which bandwidth allocation
   - Be aware that changing SPN assignments may temporarily affect connectivity
