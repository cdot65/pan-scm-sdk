# Region Models

## Overview

Region objects define geographic locations and network addresses in Palo Alto Networks' Strata Cloud Manager. These models provide the structure for creating, updating, and retrieving region configurations.

## Models

The module provides the following Pydantic models:

- `GeoLocation`: Represents the geographic coordinates of a region
- `RegionBaseModel`: Base model with fields common to all region operations
- `RegionCreateModel`: Model for creating new region objects
- `RegionUpdateModel`: Model for updating existing region objects
- `RegionResponseModel`: Response model for region operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

**Note:** The `description` and `tag` fields are included in the SDK models for consistency with other object types, but they are **not supported** by the Strata Cloud Manager API for Region objects. They will be automatically excluded when sending requests to the API.

## Component Models

### GeoLocation

The `GeoLocation` model defines the geographic coordinates of a region with valid latitude and longitude values.

| Attribute  | Type  | Required | Default | Description                                    |
|------------|-------|----------|---------|------------------------------------------------|
| latitude   | float | Yes      | -       | The latitudinal position (-90 to 90 degrees)   |
| longitude  | float | Yes      | -       | The longitudinal position (-180 to 180 degrees)|

## Base Models

### RegionBaseModel

The `RegionBaseModel` contains fields common to all region CRUD operations.

| Attribute     | Type                    | Required | Default | Description                                                     |
|---------------|-------------------------|----------|---------|-----------------------------------------------------------------|
| name          | str                     | Yes      | -       | The name of the region (max length: 64)                         |
| description   | Optional[str]           | No       | None    | A description of the region (not sent to API)                   |
| tag           | Optional[List[str]]     | No       | None    | A list of tags associated with the region (not sent to API)     |
| geo_location  | Optional[GeoLocation]   | No       | None    | The geographic location of the region                           |
| address       | Optional[List[str]]     | No       | None    | A list of addresses associated with the region                  |
| folder        | Optional[str]           | No       | None    | The folder in which the resource is defined (max length: 64)    |
| snippet       | Optional[str]           | No       | None    | The snippet in which the resource is defined (max length: 64)   |
| device        | Optional[str]           | No       | None    | The device in which the resource is defined (max length: 64)    |

!!! note
    The `address` and `tag` fields include validators that convert single strings to lists and ensure all values are unique.

#### RegionCreateModel

The `RegionCreateModel` extends the base model and includes validation to ensure that exactly one container type is provided.

| Attribute                              | Type | Required | Default | Description |
|----------------------------------------|------|----------|---------|-------------|
| *All attributes from RegionBaseModel*  |      |          |         |             |

When creating a region, exactly one container type (`folder`, `snippet`, or `device`) must be provided.

#### RegionUpdateModel

The `RegionUpdateModel` extends the base model and adds the ID field required for updating existing region objects.

| Attribute                              | Type | Required | Default | Description               |
|----------------------------------------|------|----------|---------|---------------------------|
| id                                     | UUID | Yes      | -       | The UUID of the region    |
| *All attributes from RegionBaseModel*  |      |          |         |                           |

### RegionResponseModel

The `RegionResponseModel` extends the base model and includes the ID field returned in API responses.

| Attribute                              | Type          | Required | Default | Description                                               |
|----------------------------------------|---------------|----------|---------|-----------------------------------------------------------|
| id                                     | Optional[UUID]| No       | None    | The UUID of the region (may be missing for predefined)    |
| *All attributes from RegionBaseModel*  |               |          |         |                                                           |

**Note:** The `id` field is optional because predefined regions may not have an ID.

## Usage Examples

### Creating a Region

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create a region with a geographic location
region_data = {
    "name": "us-west-region",
    "folder": "Global",
    "geo_location": {
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    "address": ["10.0.0.0/8", "192.168.1.0/24"]
}

response = client.region.create(region_data)
print(f"Created region: {response.name} (ID: {response.id})")
```

### Creating a Region in a Snippet

```python
# Create a region in a snippet
region_data = {
    "name": "europe-region",
    "snippet": "EU Configs",
    "geo_location": {
        "latitude": 51.5074,
        "longitude": -0.1278
    }
}

response = client.region.create(region_data)
```

### Updating an Existing Region

```python
# Fetch existing region
existing = client.region.fetch(name="us-west-region", folder="Global")

# Modify attributes using dot notation
existing.address = existing.address + ["172.16.0.0/16"]
existing.geo_location = {
    "latitude": 40.7128,
    "longitude": -74.0060
}

# Pass modified object to update()
updated = client.region.update(existing)
print(f"Updated region addresses: {updated.address}")
```

### Working with Response Models

```python
# List and process regions
regions = client.region.list(folder="Global")

for region in regions:
    print(f"Region: {region.name}")

    if region.id:
        print(f"  ID: {region.id}")
    else:
        print("  ID: (predefined region)")

    if region.geo_location:
        print(f"  Location: {region.geo_location.latitude}, {region.geo_location.longitude}")

    if region.address:
        print(f"  Addresses: {', '.join(region.address)}")
```

