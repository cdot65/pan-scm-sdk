# Network Locations Configuration Object

Provides read-only access to geographic network location objects in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `NetworkLocations` class provides access to network location objects representing geographic locations for service connectivity. This is a read-only resource supporting only list and fetch operations.

### Methods

| Method    | Description                          | Parameters   | Return Type                |
|-----------|--------------------------------------|--------------|----------------------------|
| `list()`  | List locations with optional filters | `**filters`  | `List[NetworkLocationModel]` |
| `fetch()` | Retrieve a location by its value     | `value: str` | `NetworkLocationModel`     |

### Model Attributes

| Attribute          | Type  | Required | Default | Description                                             |
|--------------------|-------|----------|---------|---------------------------------------------------------|
| `value`            | str   | Yes      | None    | Unique identifier for the location (e.g., "us-west-1")  |
| `display`          | str   | Yes      | None    | Human-readable location name                            |
| `continent`        | str   | No       | None    | Continent where the location exists                     |
| `region`           | str   | No       | None    | Geographic region of the location                       |
| `latitude`         | float | No       | None    | Latitude coordinate (-90 to 90)                         |
| `longitude`        | float | No       | None    | Longitude coordinate (-180 to 180)                      |
| `aggregate_region` | str   | No       | None    | Higher-level regional grouping                          |

### Exceptions

| Exception                    | HTTP Code | Description                              |
|------------------------------|-----------|------------------------------------------|
| `MissingQueryParameterError` | 400       | When value parameter is missing or empty |
| `InvalidObjectError`         | 404       | When requested location is not found     |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

locations = client.network_location
```

## Methods

### List Network Locations

```python
locations = client.network_location.list()

print(f"Found {len(locations)} network locations:")
for location in locations:
    print(f"Value: {location.value}, Display: {location.display}, Region: {location.region}")
```

**Filtering responses:**

```python
# Filter by continent
us_locations = client.network_location.list(continent="North America")

# Filter by multiple criteria
west_coast = client.network_location.list(
    continent="North America",
    aggregate_region="us-southwest"
)

# Filter by region
regions = client.network_location.list(region=["us-west2", "us-east4"])
```

**Controlling pagination with max_limit:**

```python
client.network_location.max_limit = 500

locations = client.network_location.list()
```

### Fetch a Network Location

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    location = client.network_location.fetch("us-west-1")
    print(f"Value: {location.value}")
    print(f"Display name: {location.display}")
    print(f"Continent: {location.continent}")
    print(f"Region: {location.region}")
    print(f"Coordinates: {location.latitude}, {location.longitude}")
except MissingQueryParameterError:
    print("Error: Location value cannot be empty")
except InvalidObjectError:
    print("Error: Location not found")
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    APIError
)

try:
    locations = client.network_location.list(continent="North America")
except APIError as e:
    print(f"Error retrieving network locations: {e.message}")

try:
    location = client.network_location.fetch("nonexistent-location")
except InvalidObjectError:
    print("Location not found")
except MissingQueryParameterError:
    print("Location value cannot be empty")
```

## Related Topics

- [Network Location Models](../../models/deployment/network_locations.md#Overview)
- [Deployment Overview](index.md)
- [API Client](../../client.md)
