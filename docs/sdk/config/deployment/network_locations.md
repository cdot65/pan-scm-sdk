# Network Location Configuration Object

## Table of Contents
1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Model Attributes](#model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
7. [Best Practices](#best-practices)
8. [Related Models](#related-models)

## Overview

The `NetworkLocations` class provides access to network location objects in Palo Alto Networks' Strata Cloud Manager. These objects represent geographic network locations that can be used for service connectivity and are read-only resources in the API.

## Basic Configuration

There are two approaches to configure and use the NetworkLocations service:

### Unified Client Interface (Recommended)

```python
from scm.client import Scm

# Initialize the SCM client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access network locations directly through the client
locations = client.network_location.list()
```

### Traditional Service Instantiation

```python
from scm.client import Scm
from scm.config.deployment import NetworkLocations

# Initialize the SCM client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create a NetworkLocations client instance
network_locations = NetworkLocations(client)
```

## Core Methods

| Method     | Description                           | Parameters                | Return Type               |
|------------|---------------------------------------|---------------------------|---------------------------|
| `list()`   | List locations with optional filters  | `**filters`              | `List[NetworkLocationModel]` |
| `fetch()`  | Retrieve a location by its value      | `value: str`             | `NetworkLocationModel`     |

## Model Attributes

| Attribute        | Type    | Description                                           |
|------------------|---------|-------------------------------------------------------|
| `value`          | str     | Unique identifier for the location (e.g., "us-west-1") |
| `display`        | str     | Human-readable location name                          |
| `continent`      | str     | Continent where the location exists                   |
| `region`         | str     | Geographic region of the location                     |
| `latitude`       | float   | Latitude coordinate                                   |
| `longitude`      | float   | Longitude coordinate                                  |
| `aggregate_region` | str   | Higher-level regional grouping                        |

## Exceptions

| Exception                   | HTTP Code | Description                                  |
|-----------------------------|-----------|----------------------------------------------|
| `MissingQueryParameterError` | 400      | When value parameter is missing or empty     |
| `InvalidObjectError`         | 404      | When requested location is not found         |

## Usage Examples

### List Network Locations

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.exceptions import APIError

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Get all network locations
try:
    # Using unified client approach
    locations = client.network_location.list()
    
    # Print the location values
    print(f"Found {len(locations)} network locations:")
    for location in locations:
        print(f"Value: {location.value}, Display: {location.display}, Region: {location.region}")
except APIError as e:
    print(f"Error retrieving network locations: {e.message}")
```

</div>

### Filter Network Locations

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.exceptions import APIError

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Filter locations by continent
    us_locations = client.network_location.list(continent="North America")
    print(f"Found {len(us_locations)} locations in North America")
    
    # Filter locations by multiple criteria
    west_coast = client.network_location.list(
        continent="North America", 
        aggregate_region="us-southwest"
    )
    
    # Print the results
    print(f"Found {len(west_coast)} locations in US Southwest:")
    for location in west_coast:
        print(f"Value: {location.value}, Display: {location.display}")
except APIError as e:
    print(f"Error filtering network locations: {e.message}")
```

</div>

### Fetch a Specific Network Location

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Fetch a specific network location by its value
    location = client.network_location.fetch("us-west-1")
    
    # Print the location details
    print(f"Successfully retrieved location:")
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

<!-- termynal -->

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# List all locations in Europe
europe_locations = client.network_location.list(continent="Europe")
print(f"Found {len(europe_locations)} locations in Europe")

# List specific regions
regions = client.network_location.list(region=["us-west2", "us-east4"])
print(f"Found {len(regions)} locations in specific regions")
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

<!-- termynal -->

```python
from scm.client import Scm
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch a location by its value
try:
    location = client.network_location.fetch("us-west-1")
    print(f"Found location: {location.display}")
    print(f"Continent: {location.continent}")
    print(f"Region: {location.region}")
except MissingQueryParameterError:
    print("Error: Location value cannot be empty")
except InvalidObjectError:
    print("Error: Location not found")
```

</div>

## Client Configuration

The `NetworkLocations` client can be configured with a custom maximum limit for API requests:

```python
from scm.client import Scm
from scm.config.deployment import NetworkLocations

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Option 1: Set a custom maximum limit during initialization (default is 200)
network_locations = NetworkLocations(client, max_limit=500)

# Option 2: Update it later
network_locations.max_limit = 300
```

## Best Practices

1. **API Efficiency**
   - Use filtering parameters to reduce the amount of data returned
   - Cache location data when appropriate to reduce API calls
   - Use specific filters when you know what location you're looking for

2. **Error Handling**
   - Always implement proper exception handling for `fetch()` operations
   - Validate location values before making API calls
   - Provide meaningful error messages to users

3. **Performance**
   - Consider storing frequently used location information locally
   - Limit the number of network location requests in performance-critical code paths

## Related Models

- [`NetworkLocationModel`](/sdk/models/deployment/network_locations.md)

!!! note "Read-Only Operations"
    The NetworkLocations API only supports read operations (list and fetch). Create, update, and delete operations are not available for this endpoint.
