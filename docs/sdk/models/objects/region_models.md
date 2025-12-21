# Region Models

## Overview {#Overview}

Region objects define geographic locations and network addresses in Palo Alto Networks' Strata Cloud Manager. These models provide the structure for creating, updating, and retrieving region configurations.

### Models

The module provides the following Pydantic models:

- `GeoLocation`: Represents the geographic coordinates of a region
- `RegionBaseModel`: Base model with fields common to all region operations
- `RegionCreateModel`: Model for creating new region objects
- `RegionUpdateModel`: Model for updating existing region objects
- `RegionResponseModel`: Response model for region operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

**Note:** The `description` and `tag` fields are included in the SDK models for consistency with other object types, but they are **not supported** by the Strata Cloud Manager API for Region objects. They will be automatically excluded when sending requests to the API.

## GeoLocation

The `GeoLocation` model defines the geographic coordinates of a region with valid latitude and longitude values.

| Attribute  | Type  | Required | Default | Description                                    |
|------------|-------|----------|---------|------------------------------------------------|
| latitude   | float | Yes      | -       | The latitudinal position (-90 to 90 degrees)   |
| longitude  | float | Yes      | -       | The longitudinal position (-180 to 180 degrees)|

## RegionBaseModel

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

### Field Validators

The model includes validators for the `address` and `tag` fields:

```python
@field_validator("address", "tag", mode="before")
def ensure_list_of_strings(cls, v):
    """Converts single string to list if needed."""
    if v is None:
        return v
    if isinstance(v, str):
        return [v]
    if isinstance(v, list):
        return v
    raise ValueError("Value must be a string or a list of strings")

@field_validator("address")
def ensure_unique_addresses(cls, v):
    """Ensures all addresses in the list are unique."""
    if v is not None and len(v) != len(set(v)):
        raise ValueError("List of addresses must contain unique values")
    return v

@field_validator("tag")
def ensure_unique_tags(cls, v):
    """Ensures all tags in the list are unique."""
    if v is not None and len(v) != len(set(v)):
        raise ValueError("List of tags must contain unique values")
    return v
```

## RegionCreateModel

The `RegionCreateModel` extends the base model and includes validation to ensure that exactly one container type is provided.

| Attribute                              | Type | Required | Default | Description |
|----------------------------------------|------|----------|---------|-------------|
| *All attributes from RegionBaseModel*  |      |          |         |             |

### Container Type Validation

When creating a region, exactly one of the following container types must be provided:
- `folder`: The folder in which the resource is defined
- `snippet`: The snippet in which the resource is defined
- `device`: The device in which the resource is defined

This validation is enforced by the `validate_container_type` model validator.

```python
@model_validator(mode="after")
def validate_container_type(self) -> "RegionCreateModel":
    """Validates that exactly one container type is provided."""
    container_fields = [
        "folder",
        "snippet",
        "device",
    ]
    provided = [
        field for field in container_fields if getattr(self, field) is not None
    ]
    if len(provided) != 1:
        raise ValueError(
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
        )
    return self
```

## RegionUpdateModel

The `RegionUpdateModel` extends the base model and adds the ID field required for updating existing region objects.

| Attribute                              | Type | Required | Default | Description               |
|----------------------------------------|------|----------|---------|---------------------------|
| id                                     | UUID | Yes      | -       | The UUID of the region    |
| *All attributes from RegionBaseModel*  |      |          |         |                           |

## RegionResponseModel

The `RegionResponseModel` extends the base model and includes the ID field returned in API responses.

| Attribute                              | Type          | Required | Default | Description                                               |
|----------------------------------------|---------------|----------|---------|-----------------------------------------------------------|
| id                                     | Optional[UUID]| No       | None    | The UUID of the region (may be missing for predefined)    |
| *All attributes from RegionBaseModel*  |               |          |         |                                                           |

**Note:** The `id` field is optional because predefined regions may not have an ID.

## Usage Examples

### Creating a Region

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
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

## Best Practices

### Geographic Locations
- Provide accurate latitude and longitude coordinates
- Use decimal degrees format for coordinates
- Ensure coordinates are within valid ranges (latitude: -90 to 90, longitude: -180 to 180)

### Address Management
- Use CIDR notation for IP networks (e.g., "10.0.0.0/8")
- Keep address lists concise and organized by logical grouping
- Avoid overlapping network ranges when possible
- Ensure all addresses in a region's list are unique

### Container Management
- Always specify exactly one container type (folder, snippet, or device)
- Use consistent naming conventions for regions
- Organize regions logically by geographic location or network function

### Validation
- Handle validation errors appropriately in your application
- Check for input errors, especially with latitude/longitude ranges
- Remember that predefined regions may not have an ID

## Related Models

- [Address Models](address_models.md): For defining IP addresses that can be referenced by regions
- [Tag Models](tag_models.md): For adding tags to classify and organize regions
