# Bandwidth Allocation Models

## Overview {#Overview}

The Bandwidth Allocation models provide a structured way to manage bandwidth allocation configurations in Palo Alto Networks' Strata Cloud Manager. These models allow you to create, update, and manage bandwidth allocations for different regions, supporting optional Quality of Service (QoS) configurations.

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
# Using dictionary
from scm.config.deployment import BandwidthAllocations

allocation_dict = {
    "name": "west-region",
    "allocated_bandwidth": 100,
    "spn_name_list": ["spn1", "spn2"]
}

bandwidth_allocations = BandwidthAllocations(api_client)
response = bandwidth_allocations.create(allocation_dict)

# Using model directly
from scm.models.deployment import BandwidthAllocationCreateModel

allocation = BandwidthAllocationCreateModel(
    name="west-region",
    allocated_bandwidth=100,
    spn_name_list=["spn1", "spn2"]
)

payload = allocation.model_dump(exclude_unset=True)
response = bandwidth_allocations.create(payload)
```

### Creating a Bandwidth Allocation with QoS

```python
# Using dictionary
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

response = bandwidth_allocations.create(qos_dict)

# Using model directly
from scm.models.deployment import BandwidthAllocationCreateModel, QosModel

qos = QosModel(
    enabled=True,
    customized=True,
    profile="high-priority",
    guaranteed_ratio=0.7
)

allocation = BandwidthAllocationCreateModel(
    name="east-region",
    allocated_bandwidth=200,
    spn_name_list=["spn3", "spn4"],
    qos=qos
)

payload = allocation.model_dump(exclude_unset=True)
response = bandwidth_allocations.create(payload)
```

### Updating a Bandwidth Allocation

```python
# Using dictionary
update_dict = {
    "name": "west-region",
    "allocated_bandwidth": 150,
    "spn_name_list": ["spn1", "spn2", "spn5"]
}

response = bandwidth_allocations.update(update_dict)

# Using model directly
from scm.models.deployment import BandwidthAllocationUpdateModel

update_allocation = BandwidthAllocationUpdateModel(
    name="west-region",
    allocated_bandwidth=150,
    spn_name_list=["spn1", "spn2", "spn5"]
)

payload = update_allocation.model_dump(exclude_unset=True)
response = bandwidth_allocations.update(payload)
```

### List Bandwidth Allocations

```python
# List all bandwidth allocations
all_allocations = bandwidth_allocations.list()

# Filter by name
filtered_allocations = bandwidth_allocations.list(name="west-region")

# Filter by allocated bandwidth
high_bandwidth = bandwidth_allocations.list(allocated_bandwidth=200)

# Filter by SPN name
allocations_with_spn = bandwidth_allocations.list(spn_name_list="spn1")

# Filter by QoS enabled status
qos_enabled_allocations = bandwidth_allocations.list(qos_enabled=True)
```

### Get a Single Bandwidth Allocation

```python
# Get a bandwidth allocation by name
allocation = bandwidth_allocations.get("west-region")

# Fetch will raise an exception if not found
try:
    allocation = bandwidth_allocations.fetch("west-region")
except InvalidObjectError:
    print("Bandwidth allocation not found")
```

### Delete a Bandwidth Allocation

```python
# Delete a bandwidth allocation by name and SPN name list (comma-separated)
bandwidth_allocations.delete("west-region", "spn1,spn2")
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
