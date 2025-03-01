# Region Models

Region objects define geographic locations and network addresses in Palo Alto Networks' Strata Cloud Manager. These models provide the structure for creating, updating, and retrieving region configurations.

## Models Overview

The module provides the following Pydantic models:

- `GeoLocation`: Represents the geographic coordinates of a region
- `RegionBaseModel`: Base model with fields common to all region operations
- `RegionCreateModel`: Model for creating new region objects
- `RegionUpdateModel`: Model for updating existing region objects
- `RegionResponseModel`: Response model for region operations

## GeoLocation

The `GeoLocation` model defines the geographic coordinates of a region with valid latitude and longitude values.

| Attribute  | Type  | Required | Default | Description                                    |
|------------|-------|----------|---------|------------------------------------------------|
| latitude   | float | Yes      | -       | The latitudinal position (-90 to 90 degrees)   |
| longitude  | float | Yes      | -       | The longitudinal position (-180 to 180 degrees)|

## RegionBaseModel

The `RegionBaseModel` contains fields common to all region CRUD operations.

| Attribute     | Type                    | Required | Default | Description                                                   |
|---------------|-------------------------|----------|---------|---------------------------------------------------------------|
| name          | str                     | Yes      | -       | The name of the region (max length: 31)                       |
| geo_location  | Optional[GeoLocation]   | No       | None    | The geographic location of the region                         |
| address       | Optional[List[str]]     | No       | None    | A list of addresses associated with the region                |
| folder        | Optional[str]           | No       | None    | The folder in which the resource is defined (max length: 64)  |
| snippet       | Optional[str]           | No       | None    | The snippet in which the resource is defined (max length: 64) |
| device        | Optional[str]           | No       | None    | The device in which the resource is defined (max length: 64)  |

### Address Validation

The model includes validators for the `address` field to ensure:

1. The field contains a list of strings (or can be converted to one)
2. All addresses in the list are unique

```python
@field_validator("address", mode="before")
def ensure_list_of_strings(cls, v):
    if v is None:
        return v
    if isinstance(v, str):
        return [v]
    if isinstance(v, list):
        return v
    # Catch all other types
    raise ValueError("Address must be a string or a list of strings")

@field_validator("address")
def ensure_unique_addresses(cls, v):
    if v is not None and len(v) != len(set(v)):
        raise ValueError("List of addresses must contain unique values")
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

| Attribute                              | Type | Required | Default | Description               |
|----------------------------------------|------|----------|---------|---------------------------|
| id                                     | UUID | Yes      | -       | The UUID of the region    |
| *All attributes from RegionBaseModel*  |      |          |         |                           |

## Usage Examples

### Creating a New Region

```python
from scm.models.objects.regions import RegionCreateModel, GeoLocation

# Create a region with a geographic location
region = RegionCreateModel(
    name="us-west-region",
    folder="Global",
    geo_location=GeoLocation(
        latitude=37.7749,
        longitude=-122.4194
    ),
    address=["10.0.0.0/8", "192.168.1.0/24"]
)

# Create a region without geo_location but with addresses
region_addresses_only = RegionCreateModel(
    name="internal-networks",
    folder="Global",
    address=["172.16.0.0/16", "192.168.0.0/16"]
)

# Create a region in a snippet
region_in_snippet = RegionCreateModel(
    name="europe-region",
    snippet="EU Configs",
    geo_location=GeoLocation(
        latitude=51.5074,
        longitude=-0.1278
    )
)
```

### Updating an Existing Region

```python
from uuid import UUID
from scm.models.objects.regions import RegionUpdateModel, GeoLocation

# Update an existing region
updated_region = RegionUpdateModel(
    id=UUID("123e4567-e89b-12d3-a456-426655440000"),
    name="updated-region-name",
    geo_location=GeoLocation(
        latitude=40.7128,
        longitude=-74.0060
    ),
    address=["10.0.0.0/8", "172.16.0.0/16", "192.168.0.0/16"]
)
```

### Working with Response Models

```python
from scm.models.objects.regions import RegionResponseModel

# Process a region response
def process_region(region: RegionResponseModel):
    print(f"Region ID: {region.id}")
    print(f"Region Name: {region.name}")
    
    if region.geo_location:
        print(f"Geographic Location: {region.geo_location.latitude}, {region.geo_location.longitude}")
    
    if region.address:
        print("Associated Addresses:")
        for addr in region.address:
            print(f"  - {addr}")
```

## Best Practices

### Geographic Locations
- Provide accurate latitude and longitude coordinates when defining regions
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
- Validate responses using the `RegionResponseModel`
- Handle validation errors appropriately in your application
- Check for input errors, especially with latitude/longitude ranges

## Related Models

- [Address Models](address_models.md): For defining IP addresses that can be referenced by regions
- [Tag Models](tag_models.md): For adding tags to classify and organize regions