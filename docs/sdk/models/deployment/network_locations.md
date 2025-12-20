# Network Location Models

## Overview {#Overview}

The Network Location models provide a structured way to manage network location data in Palo Alto Networks' Strata Cloud Manager. Network Locations are read-only resources that represent geographic network locations for service connectivity.

### Models

The module provides the following Pydantic model:

- `NetworkLocationModel`: Model for network location data (read-only)

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

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

| Attribute          | Type   | Required | Default | Description                                            |
|--------------------|--------|----------|---------|--------------------------------------------------------|
| `value`            | str    | Yes      | None    | The system value of the location (e.g., 'us-west-1')   |
| `display`          | str    | Yes      | None    | The human-readable display name of the location        |
| `continent`        | str    | No       | None    | The continent in which the location exists             |
| `latitude`         | float  | No       | None    | The latitudinal position of the location (-90 to 90)   |
| `longitude`        | float  | No       | None    | The longitudinal position of the location (-180 to 180)|
| `region`           | str    | No       | None    | The region code of the location                        |
| `aggregate_region` | str    | No       | None    | The aggregate region identifier                        |

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
from scm.client import ScmClient

# Initialize the client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# List network locations - returns a list of NetworkLocationModel objects
locations = client.network_location.list(continent="North America")

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
