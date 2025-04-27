# Quarantined Devices Example Script

## Overview {#Overview}

The `quarantined_devices.py` script demonstrates comprehensive examples of working with Quarantined Devices objects in Palo Alto Networks' Strata Cloud Manager (SCM). Quarantined devices are endpoints or systems that have been isolated from the network due to potential security concerns, and this script shows how to manage these devices through the SCM API.

## Features

- Creating quarantined device entries with various configurations:
  - Simple device entries with host IDs
  - Devices with serial numbers
  - Bulk creation of multiple devices
- Listing and filtering quarantined devices by:
  - Host ID
  - Serial number
- Detailed CSV report generation with device information
- Formatted output with color-coded logging
- Execution statistics and performance metrics
- Command-line arguments to customize script execution
- Robust error handling and informative messages

## Prerequisites

Before running this example script:

1. Replace the authentication credentials with your own or create a `.env` file:
   ```
   SCM_CLIENT_ID=your_client_id
   SCM_CLIENT_SECRET=your_client_secret
   SCM_TSG_ID=your_tsg_id
   SCM_LOG_LEVEL=DEBUG  # Optional
   ```

2. Make sure your SCM environment is properly set up to manage quarantined devices.

## Usage

### Basic Usage

Run the script with default settings:

```bash
python quarantined_devices.py
```

This will:
1. Create a simple quarantined device entry
2. Create a device with a serial number
3. Create multiple devices in bulk (3 by default)
4. List and filter all devices
5. Generate a CSV report
6. Clean up created devices

### Command-Line Arguments

Customize script execution with the following arguments:

```bash
python quarantined_devices.py --create --create-with-serial --skip-cleanup --bulk-count 5
```

#### Available Arguments:

- `--create`: Create simple quarantined device examples
- `--create-with-serial`: Create quarantined device examples with serial numbers
- `--bulk`: Create bulk quarantined device examples
- `--list`: List quarantined devices
- `--all`: Perform all operations (default behavior)
- `--no-report`: Skip CSV report generation
- `--skip-cleanup`: Preserve created devices (don't delete them)
- `--bulk-count BULK_COUNT`: Number of bulk devices to create (default: 3)

## Script Structure

The script is organized into several key functions:

1. `initialize_client()`: Sets up the SCM client with credentials
2. Device creation functions:
   - `create_quarantined_device()`: Creates a simple device entry
   - `create_quarantined_device_with_serial()`: Creates a device with a serial number
   - `create_bulk_devices()`: Creates multiple devices at once
3. `list_and_filter_devices()`: Demonstrates listing and filtering devices
4. `generate_devices_report()`: Creates a detailed CSV report
5. `cleanup_quarantined_devices()`: Removes created devices
6. `parse_arguments()`: Handles command-line arguments
7. `main()`: Orchestrates the overall script execution

## Example Configurations

### Simple Quarantined Device

```python
{
    "host_id": "host-abc12345"
}
```

### Quarantined Device with Serial Number

```python
{
    "host_id": "host-def67890",
    "serial_number": "PA-12345678"
}
```

## Report Generation

When executed, the script generates a comprehensive CSV report containing:

- Host IDs of quarantined devices
- Serial numbers (if provided)
- Report generation timestamp

The report is saved with a timestamp in the filename format: `quarantined_devices_report_YYYYMMDD_HHMMSS.csv`.

## Error Handling

The script includes robust error handling for:

- Authentication failures
- Invalid device configurations
- API request failures
- Missing host IDs when deleting devices
- Report generation issues

## API Integration

This example demonstrates integration with the Quarantined Devices API in Palo Alto Networks' Strata Cloud Manager. The script uses the following SDK methods:

1. `QuarantinedDevices.create()`: Create new quarantined device entries
2. `QuarantinedDevices.list()`: List and filter quarantined devices
3. `QuarantinedDevices.delete()`: Remove quarantined device entries

## Best Practices

When creating your own quarantined devices implementations, consider the following:

1. Always provide unique host IDs for each device to avoid conflicts
2. Include serial numbers where available to improve device identification
3. Implement robust error handling for API operations
4. Use filtering capabilities when managing large numbers of devices
5. Keep reports of quarantined devices for security auditing purposes

## SDK Documentation

For more information on quarantined devices, see the [Quarantined Devices Configuration](https://github.com/PaloAltoNetworks/pan-scm-sdk/blob/main/docs/sdk/config/objects/quarantined_devices.md) documentation.
