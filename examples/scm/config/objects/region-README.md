# Region Example Script

## Overview {#Overview}

The `region.py` script demonstrates comprehensive examples of working with Region objects in Palo Alto Networks' Strata Cloud Manager (SCM). Region objects define geographic locations with optional network addresses that can be used in security policies.

## Features

- Creating region objects with various configurations:
  - Regions with geographic coordinates (latitude/longitude)
  - Regions with associated network addresses
  - Regions with both coordinates and network addresses
  - Regions with tags and descriptions
- Listing and filtering region objects by:
  - Name patterns
  - Tags
  - Geographic location (latitude/longitude ranges)
  - Network addresses
- Updating existing region objects by modifying:
  - Descriptions and tags
  - Coordinates
  - Network addresses
- Bulk operations for creating multiple region objects
- Detailed CSV report generation with region object information
- Formatted output with color-coded logging
- Execution statistics and performance metrics
- Command-line arguments to customize script execution

## Prerequisites

Before running this example script:

1. Replace the authentication credentials with your own or create a `.env` file:
   ```
   SCM_CLIENT_ID=your_client_id
   SCM_CLIENT_SECRET=your_client_secret
   SCM_TSG_ID=your_tsg_id
   SCM_LOG_LEVEL=DEBUG  # Optional
   ```

2. Make sure you have a folder named "Global" in your SCM environment or modify the folder name using the `--folder` command-line argument.

## Usage

### Basic Usage

Run the script with default settings:

```bash
python region.py
```

This will:
1. Create a region with geographic coordinates
2. Create a region with network addresses
3. Create a comprehensive region with both coordinates and addresses
4. Create multiple regions in bulk
5. Update one of the created regions
6. List and filter all regions
7. Generate a CSV report
8. Clean up created regions (unless `--skip-cleanup` flag is used)

### Command-Line Arguments

Customize script execution with the following arguments:

```bash
python region.py --coordinates --comprehensive --skip-cleanup --folder "Production"
```

#### Available Arguments:

- `--coordinates`: Create only regions with geographic coordinates
- `--addresses`: Create only regions with network addresses
- `--comprehensive`: Create only regions with both coordinates and addresses
- `--bulk`: Create only bulk region examples
- `--all`: Create all region object types (default behavior)
- `--no-report`: Skip CSV report generation
- `--skip-cleanup`: Preserve created regions (don't delete them)
- `--folder FOLDER`: Folder name in SCM to create regions in (default: "Global")

## Script Structure

The script is organized into several key functions:

1. `initialize_client()`: Sets up the SCM client with credentials
2. Region creation functions:
   - `create_region_with_coordinates()`: Creates a region with geographic coordinates
   - `create_region_with_addresses()`: Creates a region with network addresses
   - `create_comprehensive_region()`: Creates a region with both coordinates and addresses
   - `create_bulk_region_objects()`: Creates multiple regions at once
3. `fetch_and_update_region()`: Demonstrates updating an existing region
4. `list_and_filter_regions()`: Shows how to list and filter regions
5. `generate_region_report()`: Creates a detailed CSV report
6. `cleanup_region_objects()`: Removes created regions
7. `parse_arguments()`: Handles command-line arguments
8. `main()`: Orchestrates the overall script execution

## Example Configurations

### Region with Geographic Coordinates

```python
{
    "name": "us-west-region",
    "description": "Example region for San Francisco metropolitan area",
    "folder": "Global",
    "tag": ["Automation", "West-Coast"],
    "geo_location": {
        "latitude": 37.7749,
        "longitude": -122.4194
    }
}
```

### Region with Network Addresses

```python
{
    "name": "corp-network",
    "description": "Example region for corporate network addresses",
    "folder": "Global",
    "tag": ["Automation", "Corporate", "Internal"],
    "address": [
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16"
    ]
}
```

### Comprehensive Region

```python
{
    "name": "nyc-region",
    "description": "Example comprehensive region for NYC area",
    "folder": "Global",
    "tag": ["Automation", "East-Coast", "Office"],
    "geo_location": {
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    "address": [
        "198.51.100.0/24",
        "203.0.113.0/24"
    ]
}
```

## Report Generation

When executed, the script generates a comprehensive CSV report containing:

- Region IDs and names
- Descriptions
- Tags
- Geographic coordinates (latitude/longitude)
- Network addresses
- Folder information
- Creation timestamps
- Report generation timestamp

The report is saved with a timestamp in the filename format: `region_objects_report_YYYYMMDD_HHMMSS.csv`.

## Filtering Examples

The script demonstrates powerful filtering capabilities:

```python
# Filter by tag
automation_tagged = regions.list(
    folder="Global",
    tag=["Automation"]
)

# Filter by name pattern (when supported)
west_regions = regions.list(
    folder="Global",
    name="west"
)

# Filter by geographic location (western hemisphere)
western_regions = regions.list(
    folder="Global",
    geo_location={
        "longitude": {"min": -180, "max": 0}
    }
)

# Filter by network address
networks_regions = regions.list(
    folder="Global",
    addresses=["10.0.0.0/8"]
)
```

## Error Handling

The script includes robust error handling for:

- Authentication failures
- Invalid region configurations
- Name conflicts
- API request failures
- Report generation issues

## Best Practices

When creating your own region implementations, consider the following:

1. Use accurate geographic coordinates for locations
2. Group related network addresses in the same region object
3. Use meaningful naming conventions (e.g., `us-west`, `eu-central`)
4. Include descriptive information in the description field
5. Use consistent tagging strategies for better organization
6. Implement proper error handling for API operations
7. Use filtering capabilities to manage large numbers of regions

## SDK Documentation

For more information on regions, see the [Region Configuration](https://github.com/PaloAltoNetworks/pan-scm-sdk/blob/main/docs/sdk/config/objects/region.md) documentation.
