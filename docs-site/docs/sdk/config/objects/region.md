# Region

The `Region` service manages region objects in Strata Cloud Manager, defining geographic locations with optional network addresses for use in security policies.

## Class Overview

The `Region` class provides CRUD operations for region objects. It is accessed through the `client.region` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Region service
regions = client.region
```

### Key Attributes

| Attribute      | Type            | Required | Description                                          |
|----------------|-----------------|----------|------------------------------------------------------|
| `name`         | `str`           | Yes      | Name of the region (max 64 chars)                    |
| `id`           | `UUID`          | No*      | UUID of the region (response only, may be missing for predefined regions) |
| `geo_location` | `GeoLocation`   | No       | Geographic coordinates (latitude/longitude)          |
| `address`      | `List[str]`     | No       | List of addresses associated with the region         |
| `folder`       | `str`           | Yes**    | Folder location (**one container required)           |
| `snippet`      | `str`           | Yes**    | Snippet location (**one container required)          |
| `device`       | `str`           | Yes**    | Device location (**one container required)           |

\* Exactly one of `folder`, `snippet`, or `device` is required.

#### GeoLocation Attributes

| Attribute   | Type    | Required | Description                         |
|-------------|---------|----------|-------------------------------------|
| `latitude`  | `float` | Yes      | Latitudinal position (-90 to 90)    |
| `longitude` | `float` | Yes      | Longitudinal position (-180 to 180) |

## Methods

### List Regions

Retrieves a list of region objects with optional filtering.

```python
regions = client.region.list(folder="Texas")

for region in regions:
    print(f"Region: {region.name}")
    if region.geo_location:
        print(f"  Location: {region.geo_location.latitude}, {region.geo_location.longitude}")
```

### Fetch a Region

Retrieves a single region by name and container.

```python
region = client.region.fetch(name="us-west-region", folder="Texas")
print(f"Found region: {region.name}")
```

### Create a Region

Creates a new region object.

```python
new_region = client.region.create({
    "name": "us-west-region",
    "folder": "Texas",
    "geo_location": {
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    "address": ["192.168.1.0/24", "192.168.2.0/24"]
})
```

### Update a Region

Updates an existing region object.

```python
existing = client.region.fetch(name="us-west-region", folder="Texas")
existing.address = existing.address + ["192.168.3.0/24"]
existing.geo_location = {"latitude": 40.7128, "longitude": -74.0060}

updated = client.region.update(existing)
```

### Delete a Region

Deletes a region by ID.

```python
client.region.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Creating Regions with Geographic Coordinates

Define regions with both geographic locations and network addresses.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Region with coordinates and addresses
client.region.create({
    "name": "datacenter-east",
    "folder": "Texas",
    "geo_location": {
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    "address": ["192.168.10.0/24", "192.168.20.0/24"]
})

# Region with addresses only
client.region.create({
    "name": "internal-networks",
    "folder": "Texas",
    "address": ["172.16.0.0/16", "192.168.0.0/16"]
})
```

### Geographic Filtering

Filter regions by geographic location range.

```python
# Find regions in a specific area
west_coast = client.region.list(
    folder="Texas",
    geo_location={
        "latitude": {"min": 30, "max": 50},
        "longitude": {"min": -130, "max": -110}
    }
)

# Filter by addresses
filtered = client.region.list(
    folder="Texas",
    addresses=["192.168.1.0/24"]
)

# Combine filters with exclusions
combined = client.region.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["Test", "Development"]
)
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_region = client.region.create({
        "name": "test-region",
        "geo_location": {
            "latitude": 100,  # Invalid: exceeds 90
            "longitude": -122.4194
        },
        "folder": "Texas"
    })
except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")

try:
    region = client.region.fetch(name="test", folder="")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")
```

## Related Topics

- [Region Models](../../models/objects/region_models.md)
- [Address](address.md)
