# Network Location Models

This section covers the Pydantic models used for working with Network Locations in the Strata Cloud Manager API.

## NetworkLocationModel

The `NetworkLocationModel` is used to represent network location data returned from the Strata Cloud Manager API.

```python
from scm.models.deployment import NetworkLocationModel

# Example usage
location = NetworkLocationModel(
    value="us-west-1",
    display="US West",
    continent="North America",
    latitude=37.7749,
    longitude=-122.4194,
    region="us-west2",
    aggregate_region="us-southwest"
)
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `value` | `str` | The system value of the location (e.g., 'us-west-1') |
| `display` | `str` | The human-readable display name of the location |
| `continent` | `Optional[str]` | The continent in which the location exists |
| `latitude` | `Optional[float]` | The latitudinal position of the location (-90 to 90) |
| `longitude` | `Optional[float]` | The longitudinal position of the location (-180 to 180) |
| `region` | `Optional[str]` | The region code of the location |
| `aggregate_region` | `Optional[str]` | The aggregate region identifier |

### Example Data

Here's an example of the data structure for a network location:

```json
{
  "value": "us-west-1",
  "display": "US West",
  "continent": "North America",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "region": "us-west2",
  "aggregate_region": "us-southwest"
}
```

## Usage with the API Client

The model is used automatically when retrieving network locations using the SDK:

```python
from scm.client import Scm
from scm.config.deployment import NetworkLocations

# Initialize the client
client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tsg-id"
)

# Create a NetworkLocations client instance
network_locations = NetworkLocations(client)

# List network locations - returns a list of NetworkLocationModel objects
locations = network_locations.list(continent="North America")

# Access model attributes
for location in locations:
    print(f"Value: {location.value}")
    print(f"Display: {location.display}")
    print(f"Region: {location.region}")
    print(f"Coordinates: {location.latitude}, {location.longitude}")
    print("---")
```

!!! note "Read-Only Model"
    Network Locations are read-only resources in the Strata Cloud Manager API. The model is used for receiving data only and cannot be used for creating or updating resources.
