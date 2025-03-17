# Network Locations

The `NetworkLocations` class provides access to network location objects in Palo Alto Networks' Strata Cloud Manager.

## Initialization

```python
from scm.client import Scm
from scm.config.deployment import NetworkLocations

# Initialize the SCM client
client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tsg-id"
)

# Create a NetworkLocations client instance
network_locations = NetworkLocations(client)
```

## Available Methods

The NetworkLocations client provides the following methods:

| Method  | Description                                               |
|---------|-----------------------------------------------------------|
| `list`  | List all network location objects with optional filtering |
| `fetch` | Fetch a single network location by its value              |

## Example Usage

### List Network Locations

<div class="termy">

```python
# Get all network locations
locations = network_locations.list()

# Print the location values
for location in locations:
    print(f"Value: {location.value}, Display: {location.display}, Region: {location.region}")
```

</div>

### Filter Network Locations

<div class="termy">

```python
# Filter locations by continent
us_locations = network_locations.list(continent="North America")

# Filter locations by multiple criteria
west_coast = network_locations.list(
    continent="North America", 
    aggregate_region="us-southwest"
)

# Print the results
for location in west_coast:
    print(f"Value: {location.value}, Display: {location.display}")
```

</div>

### Fetch a Specific Network Location

<div class="termy">

```python
# Fetch a specific network location by its value
location = network_locations.fetch("us-west-1")

# Print the location details
print(f"Value: {location.value}")
print(f"Display name: {location.display}")
print(f"Continent: {location.continent}")
print(f"Region: {location.region}")
print(f"Coordinates: {location.latitude}, {location.longitude}")
```

</div>

## Method Details

### list

```python
def list(**filters) -> List[NetworkLocationModel]:
```

Lists network location objects with optional filtering.

**Parameters:**

- **filters**: Keyword arguments for filtering the results
  - `value`: Filter by location value (string or list)
  - `display`: Filter by display name (string or list)
  - `region`: Filter by region (string or list)
  - `continent`: Filter by continent (string or list)
  - `aggregate_region`: Filter by aggregate region (string or list)

**Returns:**

- List of `NetworkLocationModel` objects matching the filters

**Example:**

<div class="termy">

```python
# List all locations in Europe
europe_locations = network_locations.list(continent="Europe")

# List specific regions
regions = network_locations.list(region=["us-west2", "us-east4"])
```

</div>

### fetch

```python
def fetch(value: str) -> NetworkLocationModel:
```

Fetches a single network location by its value.

**Parameters:**

- `value`: The system value of the network location to fetch (e.g., "us-west-1")

**Returns:**

- `NetworkLocationModel` object if found

**Raises:**

- `MissingQueryParameterError`: If the value is empty
- `InvalidObjectError`: If no location with the given value is found

**Example:**

<div class="termy">

```python
# Fetch a location by its value
try:
    location = network_locations.fetch("us-west-1")
    print(f"Found location: {location.display}")
except InvalidObjectError:
    print("Location not found")
```

</div>

## Client Configuration

The `NetworkLocations` client can be configured with a custom maximum limit for API requests:

```python
# Set a custom maximum limit (default is 200)
network_locations = NetworkLocations(client, max_limit=500)

# Or update it later
network_locations.max_limit = 300
```

!!! note "Read-Only Operations"
    The NetworkLocations API only supports read operations (list and fetch). Create, update, and delete operations are not available for this endpoint.
