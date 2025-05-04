# Device Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Device Model Attributes](#device-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Listing Devices](#listing-devices)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Full Script Examples](#full-script-examples)
10. [Related Models](#related-models)

## Overview

The `Device` class provides methods for listing, filtering, and managing device resources in Palo Alto Networks' Strata Cloud Manager. It supports server-side and client-side filtering, pagination, and device-specific operations.

## Core Methods

| Method     | Description                  | Parameters                      | Return Type                     |
|------------|------------------------------|----------------------------------|---------------------------------|
| `list()`   | Lists devices with filtering | `**filters`                     | `List[DeviceResponseModel]`     |

## Device Model Attributes

| Attribute           | Type                | Description                                        |
|---------------------|---------------------|----------------------------------------------------|
| `id`                | UUID                | Unique device identifier (serial number)           |
| `name`              | str                 | Device name                                        |
| `serial_number`     | str                 | Serial number                                      |
| `model`             | str                 | Device model (e.g., 'PA-VM')                       |
| `type`              | str                 | Device type (e.g., 'vm', 'firewall', 'panorama')   |
| `available_licenses`| List[Dict]          | List of available licenses                         |
| `installed_licenses`| List[Dict]          | List of installed licenses                         |

## Exceptions

| Exception                | HTTP Code | Description                                   |
|--------------------------|-----------|-----------------------------------------------|
| `InvalidObjectError`     | 400       | Invalid device data or format                 |
| `ObjectNotPresentError`  | 404       | Requested device not found                    |
| `APIError`               | Various   | General API communication error               |
| `AuthenticationError`    | 401       | Authentication failed                         |
| `ServerError`            | 500       | Internal server error                         |

## Basic Configuration

The Device service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Device service directly through the client
# No need to create a separate Device instance
devices = client.device
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.setup.device import Device

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Device object explicitly
devices = Device(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Listing Devices
```python
# List all devices
all_devices = devices.list()

for device in all_devices:
    print(device.id, device.name, device.model)
```

### Filtering Responses
```python
# Filter devices by type
vm_devices = devices.list(type="vm")

# Filter devices by serial number
specific_device = devices.list(serial_number="001122334455")

# Filter devices by model
pa_devices = devices.list(model="PA-VM")

# Filter device-only resources
device_only = devices.list(device_only=True)
```

### Controlling Pagination with max_limit
```python
devices = Device(client, max_limit=100)
results = devices.list()
```

## Error Handling

```python
from scm.exceptions import ObjectNotPresentError, InvalidObjectError, APIError

try:
    devices.list(type="invalid-type")
except InvalidObjectError as e:
    print("Invalid device type:", e)
except APIError as e:
    print("API error occurred:", e)
```

## Best Practices
- Use server-side filters when possible for better performance.
- Apply additional client-side filtering for more complex queries.
- Handle exceptions for robust automation.
- Use pagination (`max_limit`) for large device sets.
- Always specify the exact filter parameters to narrow results.

## Full Script Examples

```python
from scm.client import Scm
from scm.config.setup.device import Device
from scm.exceptions import APIError

# Initialize the client and service
client = Scm(api_key="your-api-key")
devices = Device(client)

try:
    # Get all VM firewalls
    vm_firewalls = devices.list(type="vm")
    
    print(f"Found {len(vm_firewalls)} VM firewalls:")
    
    for device in vm_firewalls:
        print(f"ID: {device.id}")
        print(f"Name: {device.name}")
        print(f"Model: {device.model}")
        print(f"Serial: {device.serial_number}")
        
        # Display licenses
        if device.installed_licenses:
            print("Installed licenses:")
            for license in device.installed_licenses:
                print(f"  - {license.get('name')}")
        
        print("---")
        
except APIError as e:
    print(f"Error retrieving devices: {e}")
```

## Related Models
- See [Device Models](../../models/setup/device_models.md) for model details.