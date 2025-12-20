# Quarantined Devices Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Quarantined Device Model Attributes](#quarantined-device-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Quarantined Devices](#creating-quarantined-devices)
    - [Listing Quarantined Devices](#listing-quarantined-devices)
    - [Deleting Quarantined Devices](#deleting-quarantined-devices)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Full Script Examples](#full-script-examples)
10. [Related Models](#related-models)

## Overview

The `QuarantinedDevices` class provides functionality to manage quarantined devices in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, listing, and deleting quarantined device entries.

Note: This service does not support `get()`, `update()`, or `fetch()` methods. Quarantined devices are identified by their `host_id` and can be listed with optional filters or deleted by `host_id`.

## Core Methods

| Method     | Description                                | Parameters                                                   | Return Type                            |
|------------|--------------------------------------------|--------------------------------------------------------------|----------------------------------------|
| `create()` | Creates a new quarantined device           | `data: Dict[str, Any]`                                       | `QuarantinedDevicesResponseModel`      |
| `list()`   | Lists quarantined devices with filtering   | `host_id: Optional[str]`, `serial_number: Optional[str]`     | `List[QuarantinedDevicesResponseModel]`|
| `delete()` | Deletes a quarantined device by host ID    | `host_id: str`                                               | `None`                                 |

## Quarantined Device Model Attributes

| Attribute       | Type | Required | Default | Description               |
|-----------------|------|----------|---------|---------------------------|
| `host_id`       | str  | Yes      | None    | Device host ID            |
| `serial_number` | str  | No       | None    | Device serial number      |

## Exceptions

| Exception                    | HTTP Code | Description                          |
|------------------------------|-----------|--------------------------------------|
| `InvalidObjectError`         | 400       | Invalid request payload              |
| `MissingQueryParameterError` | 400       | Missing required host_id parameter   |
| `InvalidObjectError`         | 500       | Invalid response format from the API |

## Basic Configuration

```python
from scm.client import ScmClient

# Initialize client using the unified client approach
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the quarantined_device module directly through the client
# client.quarantined_device is automatically initialized for you
```

You can also use the traditional approach if preferred:

```python
from scm.client import Scm
from scm.config.objects import QuarantinedDevices

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize QuarantinedDevices object
quarantined_devices = QuarantinedDevices(client)
```

## Usage Examples

### Creating Quarantined Devices

```python
# Create a new quarantined device with required fields only
device_data = {
    "host_id": "abc123"
}

new_device = client.quarantined_device.create(device_data)
print(f"Created quarantined device with host ID: {new_device.host_id}")

# Create a quarantined device with all fields
device_data_full = {
    "host_id": "device-12345",
    "serial_number": "PA-987654321"
}

new_device = client.quarantined_device.create(device_data_full)
print(f"Created device: {new_device.host_id}, Serial: {new_device.serial_number}")
```

### Listing Quarantined Devices

```python
# List all quarantined devices
all_devices = client.quarantined_device.list()
print(f"Found {len(all_devices)} quarantined devices")

for device in all_devices:
    print(f"Host ID: {device.host_id}, Serial: {device.serial_number}")

# List quarantined devices with a specific host ID
filtered_by_host = client.quarantined_device.list(host_id="abc123")
print(f"Found {len(filtered_by_host)} devices with host ID 'abc123'")

# List quarantined devices with a specific serial number
filtered_by_serial = client.quarantined_device.list(serial_number="PA-123456789")
print(f"Found {len(filtered_by_serial)} devices with serial number 'PA-123456789'")

# List with both filters applied
filtered_devices = client.quarantined_device.list(
    host_id="abc123",
    serial_number="PA-123456789"
)
print(f"Found {len(filtered_devices)} devices matching both filters")
```

### Deleting Quarantined Devices

```python
# Delete a quarantined device by host ID
client.quarantined_device.delete("abc123")
print("Device deleted successfully")

# Delete with error handling
try:
    client.quarantined_device.delete("device-to-delete")
    print("Device deleted successfully")
except Exception as e:
    print(f"Error deleting device: {e}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Attempt to create a quarantined device
    device_data = {
        "host_id": "device-12345",
        "serial_number": "PA-987654321"
    }

    new_device = client.quarantined_device.create(device_data)
    print(f"Created device: {new_device.host_id}")

except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"HTTP status: {e.http_status_code}")
    print(f"Details: {e.details}")

try:
    # Attempt to delete with an empty host_id
    client.quarantined_device.delete("")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")
```

## Best Practices

### Client Usage

- Use the unified `ScmClient` approach for simpler code
- Access quarantined device operations via `client.quarantined_device` property
- Initialize the client once and reuse across different object types

### Device Management

- Always provide a valid `host_id` when creating quarantined devices
- Use the `serial_number` field when available for better device identification
- Verify device existence before deletion using the `list()` method

### Error Handling

- Always handle specific exceptions (`InvalidObjectError`, `MissingQueryParameterError`)
- Implement retry logic for transient network errors
- Log detailed error information for troubleshooting
- Validate `host_id` is not empty before calling `delete()`

### Performance

- Use filters when listing to reduce response size
- Combine `host_id` and `serial_number` filters for precise queries

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

# Create a new quarantined device
new_device_data = {
    "host_id": "device-12345",
    "serial_number": "PA-987654321"
}

try:
    # Create the device
    new_device = client.quarantined_device.create(new_device_data)
    print(f"Created quarantined device: {new_device.host_id}")

    # List all quarantined devices
    all_devices = client.quarantined_device.list()
    print(f"Total quarantined devices: {len(all_devices)}")

    # List devices with filters
    filtered_devices = client.quarantined_device.list(serial_number="PA-987654321")
    print(f"Found {len(filtered_devices)} devices with specified serial number")

    # Delete the device we just created
    client.quarantined_device.delete(new_device.host_id)
    print(f"Deleted quarantined device: {new_device.host_id}")

    # Verify deletion
    remaining_devices = client.quarantined_device.list(host_id=new_device.host_id)
    print(f"Devices remaining after deletion: {len(remaining_devices)}")

except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Related Models

- [QuarantinedDevicesCreateModel](../../models/objects/quarantined_devices_models.md#Overview)
- [QuarantinedDevicesResponseModel](../../models/objects/quarantined_devices_models.md#Overview)
- [QuarantinedDevicesListParamsModel](../../models/objects/quarantined_devices_models.md#Overview)
