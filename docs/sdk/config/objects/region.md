# Region

The Region service provides a way to manage region objects in Palo Alto Networks' Strata Cloud Manager. Region objects define geographic locations with optional network addresses that can be used in security policies.

## Client Initialization

```python
from scm.client import Scm

# Initialize the unified client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the region service through the client
region_service = client.region
```

## Basic Operations

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
```

### Retrieving a Region by ID

```python
# Get a region by its ID
region_id = "123e4567-e89b-12d3-a456-426655440000"
region = client.region.get(region_id)
print(f"Retrieved region: {region.name}")
print(f"Geographic location: {region.geo_location.latitude}, {region.geo_location.longitude}")
```

### Fetching a Region by Name

```python
# Fetch a region by name and container
region = client.region.fetch(name="us-west-region", folder="Global")
print(f"Fetched region ID: {region.id}")

# You can also fetch from a snippet or device
region_in_snippet = client.region.fetch(name="europe-region", snippet="EU Configs")
```

### Updating a Region

```python
from scm.models.objects import RegionUpdateModel
from uuid import UUID

# Retrieve existing region first
region = client.region.get("123e4567-e89b-12d3-a456-426655440000")

# Create update model with modifications
update_data = RegionUpdateModel(
    id=UUID(region.id),
    name=region.name,
    geo_location={
        "latitude": 40.7128,  # Updated latitude
        "longitude": -74.0060  # Updated longitude
    },
    address=region.address + ["172.16.0.0/16"]  # Add a new network
)

# Update the region
updated_region = client.region.update(update_data)
print(f"Updated region with new addresses: {updated_region.address}")
```

### Deleting a Region

```python
# Delete a region by ID
region_id = "123e4567-e89b-12d3-a456-426655440000"
client.region.delete(region_id)
print(f"Deleted region with ID: {region_id}")
```

## Listing and Filtering

### List All Regions in a Container

```python
# List all regions in a folder
regions = client.region.list(folder="Global")
print(f"Found {len(regions)} regions in the Global folder")

# List regions in a snippet
snippet_regions = client.region.list(snippet="EU Configs")
```

### Filtering by Geographic Location

```python
# Filter regions by geographic location (west coast US)
filtered_regions = client.region.list(
    folder="Global",
    geo_location={
        "latitude": {"min": 30, "max": 50},
        "longitude": {"min": -130, "max": -110}
    }
)
print(f"Found {len(filtered_regions)} regions in the west coast US area")
```

### Filtering by Network Addresses

```python
# Filter regions that include a specific address range
filtered_regions = client.region.list(
    folder="Global",
    addresses=["10.0.0.0/8"]
)
print(f"Found {len(filtered_regions)} regions containing the 10.0.0.0/8 network")
```

### Container-Based Filtering

```python
# List regions with exact container matching
exact_regions = client.region.list(folder="Global", exact_match=True)

# List regions excluding specific folders
filtered_regions = client.region.list(
    folder="Global",
    exclude_folders=["Test", "Development"]
)

# List regions excluding specific snippets
filtered_regions = client.region.list(
    folder="Global",
    exclude_snippets=["Test Snippet"]
)
```

## Advanced Usage

### Combining Multiple Filters

```python
# Combine geographic location and address filtering
combined_filtered_regions = client.region.list(
    folder="Global",
    geo_location={
        "latitude": {"min": 30, "max": 50},
        "longitude": {"min": -130, "max": -110}
    },
    addresses=["10.0.0.0/8"],
    exclude_folders=["Test"]
)
```

### Paginated Listing with Custom Limit

```python
# Create region service with custom pagination limit
region_service_with_limit = client.region
region_service_with_limit.max_limit = 1000  # Set maximum items per page

# Now list will use the custom limit for pagination
regions = region_service_with_limit.list(folder="Global")
```

## Related Documentation

- [Region Models](../../models/objects/region_models.md) - Learn about the Pydantic models for Region objects
- [Address](address.md) - Manage IP and FQDN address objects that can be associated with regions