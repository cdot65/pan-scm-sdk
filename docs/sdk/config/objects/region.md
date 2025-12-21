# Region Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Region Model Attributes](#region-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating a Region](#creating-a-region)
    - [Retrieving a Region](#retrieving-a-region)
    - [Updating a Region](#updating-a-region)
    - [Listing Regions](#listing-regions)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting a Region](#deleting-a-region)
7. [Managing Configuration Changes](#managing-configuration-changes)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `Region` class provides functionality to manage region objects in Palo Alto Networks' Strata Cloud Manager. Region objects define geographic locations with optional network addresses that can be used in security policies. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, listing, and deleting region configurations.

**Note:** While the SDK models support `description` and `tag` fields for consistency with other object types, these fields are **not supported** by the Strata Cloud Manager API for Region objects. They will be automatically excluded when sending requests to the API.

## Core Methods

| Method     | Description                         | Parameters                                           | Return Type                  |
|------------|-------------------------------------|------------------------------------------------------|------------------------------|
| `create()` | Creates a new region object         | `data: Dict[str, Any]`                               | `RegionResponseModel`        |
| `get()`    | Retrieves a region by ID            | `object_id: str`                                     | `RegionResponseModel`        |
| `update()` | Updates an existing region          | `region: RegionUpdateModel`                          | `RegionResponseModel`        |
| `delete()` | Deletes a region                    | `object_id: str`                                     | `None`                       |
| `list()`   | Lists regions with optional filters | See [List Method Parameters](#list-method-parameters)| `List[RegionResponseModel]`  |
| `fetch()`  | Retrieves a single region by name   | See [Fetch Method Parameters](#fetch-method-parameters)| `RegionResponseModel`      |

### List Method Parameters

| Parameter          | Type                | Required | Default | Description                                                   |
|--------------------|---------------------|----------|---------|---------------------------------------------------------------|
| `folder`           | Optional[str]       | No*      | None    | Folder in which the resource is defined                       |
| `snippet`          | Optional[str]       | No*      | None    | Snippet in which the resource is defined                      |
| `device`           | Optional[str]       | No*      | None    | Device in which the resource is defined                       |
| `exact_match`      | bool                | No       | False   | If True, only return objects whose container exactly matches  |
| `exclude_folders`  | Optional[List[str]] | No       | None    | List of folder names to exclude from results                  |
| `exclude_snippets` | Optional[List[str]] | No       | None    | List of snippet values to exclude from results                |
| `exclude_devices`  | Optional[List[str]] | No       | None    | List of device values to exclude from results                 |
| `**filters`        | Any                 | No       | None    | Additional filters: `geo_location` (dict), `addresses` (list) |

\* Exactly one of `folder`, `snippet`, or `device` must be provided.

### Fetch Method Parameters

| Parameter | Type          | Required | Default | Description                              |
|-----------|---------------|----------|---------|------------------------------------------|
| `name`    | str           | Yes      | -       | The name of the region to fetch          |
| `folder`  | Optional[str] | No*      | None    | Folder in which the resource is defined  |
| `snippet` | Optional[str] | No*      | None    | Snippet in which the resource is defined |
| `device`  | Optional[str] | No*      | None    | Device in which the resource is defined  |

\* Exactly one of `folder`, `snippet`, or `device` must be provided.

## Region Model Attributes

| Attribute      | Type                  | Required | Default | Description                                              |
|----------------|-----------------------|----------|---------|----------------------------------------------------------|
| `name`         | str                   | Yes      | None    | The name of the region (max length: 64)                  |
| `id`           | UUID                  | No*      | None    | The UUID of the region (response only)                   |
| `geo_location` | GeoLocation           | No       | None    | Geographic coordinates (latitude/longitude)              |
| `address`      | List[str]             | No       | None    | List of addresses associated with the region             |
| `folder`       | str                   | No**     | None    | The folder in which the resource is defined (max: 64)    |
| `snippet`      | str                   | No**     | None    | The snippet in which the resource is defined (max: 64)   |
| `device`       | str                   | No**     | None    | The device in which the resource is defined (max: 64)    |

\* The `id` field is optional in responses (may be missing for predefined regions).
\*\* Exactly one container type must be provided for create operations.

### GeoLocation Attributes

| Attribute   | Type  | Required | Default | Description                              |
|-------------|-------|----------|---------|------------------------------------------|
| `latitude`  | float | Yes      | -       | Latitudinal position (-90 to 90)         |
| `longitude` | float | Yes      | -       | Longitudinal position (-180 to 180)      |

## Exceptions

| Exception                    | HTTP Code | Description                                                 |
|------------------------------|-----------|-------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid request data or parameters                          |
| `MissingQueryParameterError` | 400       | Missing required parameter (e.g., empty name or folder)     |
| `InvalidObjectError`         | 500       | Invalid response format from the API                        |

## Basic Configuration

```python
from scm.client import ScmClient

# Initialize client using the unified client approach
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the region service directly through the client
# client.region is automatically initialized for you
```

## Usage Examples

### Creating a Region

```python
# Create a region with geographic coordinates
region_data = {
    "name": "us-west-region",
    "folder": "Global",
    "geo_location": {
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    "address": ["10.0.0.0/8", "192.168.1.0/24"]
}

new_region = client.region.create(region_data)
print(f"Created region {new_region.name} with ID: {new_region.id}")

# Create a region with addresses only (no geo_location)
region_addresses = {
    "name": "internal-networks",
    "folder": "Global",
    "address": ["172.16.0.0/16", "192.168.0.0/16"]
}

new_region = client.region.create(region_addresses)
```

### Retrieving a Region

```python
# Get a region by its ID
region_id = "123e4567-e89b-12d3-a456-426655440000"
region = client.region.get(region_id)
print(f"Retrieved region: {region.name}")

if region.geo_location:
    print(f"Location: {region.geo_location.latitude}, {region.geo_location.longitude}")

# Fetch a region by name and container
region = client.region.fetch(name="us-west-region", folder="Global")
print(f"Fetched region ID: {region.id}")

# Fetch from a snippet
region_in_snippet = client.region.fetch(name="europe-region", snippet="EU Configs")
```

### Updating a Region

```python
# Fetch existing region
existing_region = client.region.fetch(name="us-west-region", folder="Global")

# Modify attributes using dot notation
existing_region.address = existing_region.address + ["172.16.0.0/16"]

# Update geo_location
existing_region.geo_location = {
    "latitude": 40.7128,
    "longitude": -74.0060
}

# Perform update
updated_region = client.region.update(existing_region)
print(f"Updated region with new addresses: {updated_region.address}")
```

### Listing Regions

```python
# List all regions in a folder
regions = client.region.list(folder="Global")
print(f"Found {len(regions)} regions")

for region in regions:
    print(f"  - {region.name}")

# List regions in a snippet
snippet_regions = client.region.list(snippet="EU Configs")

# List with exact container match
exact_regions = client.region.list(folder="Global", exact_match=True)

# List with exclusions
filtered_regions = client.region.list(
    folder="Global",
    exclude_folders=["Test", "Development"]
)
```

### Filtering Responses

```python
# Filter regions by geographic location range
west_coast_regions = client.region.list(
    folder="Global",
    geo_location={
        "latitude": {"min": 30, "max": 50},
        "longitude": {"min": -130, "max": -110}
    }
)
print(f"Found {len(west_coast_regions)} regions in the west coast area")

# Filter regions by network addresses
filtered_regions = client.region.list(
    folder="Global",
    addresses=["10.0.0.0/8"]
)
print(f"Found {len(filtered_regions)} regions containing 10.0.0.0/8")

# Combine multiple filters
combined_filtered = client.region.list(
    folder="Global",
    geo_location={
        "latitude": {"min": 30, "max": 50},
        "longitude": {"min": -130, "max": -110}
    },
    addresses=["10.0.0.0/8"],
    exclude_folders=["Test"]
)
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method automatically paginates through all objects.

```python
# Configure max_limit on the region service
client.region.max_limit = 1000

# List all regions - auto-paginates through results
all_regions = client.region.list(folder="Global")
print(f"Retrieved {len(all_regions)} regions")
```

### Deleting a Region

```python
# Delete a region by ID
region_id = "123e4567-e89b-12d3-a456-426655440000"
client.region.delete(region_id)
print(f"Deleted region with ID: {region_id}")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Global"],
    "description": "Updated region configurations",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = client.commit(**commit_params)
print(f"Commit job ID: {result.job_id}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Attempt to create a region with invalid data
    region_data = {
        "name": "test-region",
        "geo_location": {
            "latitude": 100,  # Invalid: exceeds 90
            "longitude": -122.4194
        },
        "folder": "Global"
    }
    new_region = client.region.create(region_data)
except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"HTTP status: {e.http_status_code}")
    print(f"Details: {e.details}")

try:
    # Attempt to fetch with empty folder
    region = client.region.fetch(name="test", folder="")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")

try:
    # Attempt to list without container
    regions = client.region.list()
except InvalidObjectError as e:
    print(f"Container error: {e.message}")
```

## Best Practices

### Client Usage

- Use the unified `ScmClient` interface for simpler code
- Access region operations via `client.region` property
- Initialize the client once and reuse across operations

### Geographic Locations

- Provide accurate latitude and longitude coordinates
- Use decimal degrees format for coordinates
- Ensure coordinates are within valid ranges (latitude: -90 to 90, longitude: -180 to 180)

### Address Management

- Use CIDR notation for IP networks (e.g., "10.0.0.0/8")
- Keep address lists concise and organized
- Avoid overlapping network ranges when possible
- Ensure all addresses in a region's list are unique

### Container Management

- Always specify exactly one container type (folder, snippet, or device)
- Use consistent naming conventions for regions
- Organize regions logically by geographic location or network function

### Performance

- Set an appropriate `max_limit` for large datasets
- Use specific filters to reduce response size
- Use `exact_match=True` when you know the exact container path

### Error Handling

- Always handle specific exceptions (`InvalidObjectError`, `MissingQueryParameterError`)
- Implement retry logic for transient network errors
- Log detailed error information for troubleshooting

## Full Script Examples

```python
from scm.client import ScmClient
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

# Initialize the unified client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Create a new region with geo_location and addresses
    region_data = {
        "name": "datacenter-east",
        "folder": "Global",
        "geo_location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "address": ["10.10.0.0/16", "10.20.0.0/16"]
    }

    new_region = client.region.create(region_data)
    print(f"Created region: {new_region.name} (ID: {new_region.id})")

    # Fetch and update the region
    existing = client.region.fetch(name="datacenter-east", folder="Global")
    existing.address = existing.address + ["10.30.0.0/16"]
    updated = client.region.update(existing)
    print(f"Updated region addresses: {updated.address}")

    # List all regions with geographic filtering
    west_regions = client.region.list(
        folder="Global",
        geo_location={
            "latitude": {"min": 30, "max": 50},
            "longitude": {"min": -130, "max": -110}
        }
    )
    print(f"Found {len(west_regions)} regions in western US")

    # Clean up - delete the region
    client.region.delete(str(new_region.id))
    print(f"Deleted region: {new_region.name}")

except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Related Models

- [Region Models](../../models/objects/region_models.md) - Pydantic models for region objects
- [Address Configuration](address.md) - Manage IP and FQDN address objects
