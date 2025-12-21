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

| Method     | Description                  | Parameters                       | Return Type                     |
|------------|------------------------------|----------------------------------|---------------------------------|
| `get()`    | Retrieves a device by ID     | `device_id: str`                 | `DeviceResponseModel`           |
| `fetch()`  | Gets device by name          | `name: str`                      | `DeviceResponseModel` or `None` |
| `list()`   | Lists devices with filtering | `**filters`                      | `List[DeviceResponseModel]`     |

## Device Model Attributes

### Base Attributes

| Attribute           | Type                       | Required | Default | Description                              |
|---------------------|----------------------------|----------|---------|------------------------------------------|
| `name`              | str                        | No       | None    | Device name                              |
| `display_name`      | str                        | No       | None    | Display name for the device              |
| `serial_number`     | str                        | No       | None    | Device serial number                     |
| `family`            | str                        | No       | None    | Device family (e.g., 'vm')               |
| `model`             | str                        | No       | None    | Device model (e.g., 'PA-VM')             |
| `folder`            | str                        | No       | None    | Folder name containing the device        |
| `hostname`          | str                        | No       | None    | Device hostname                          |
| `type`              | str                        | No       | None    | Device type (e.g., 'on-prem')            |
| `device_only`       | bool                       | No       | None    | True if device-only entry                |
| `is_connected`      | bool                       | No       | None    | Connection status                        |
| `description`       | str                        | No       | None    | Device description                       |

### Response-Only Attributes

| Attribute              | Type                       | Required | Default | Description                           |
|------------------------|----------------------------|----------|---------|---------------------------------------|
| `id`                   | str                        | Yes      | None    | Unique device identifier              |
| `connected_since`      | str                        | No       | None    | ISO timestamp when connected          |
| `software_version`     | str                        | No       | None    | Software version                      |
| `ip_address`           | str                        | No       | None    | IPv4 address                          |
| `ipV6_address`         | str                        | No       | None    | IPv6 address                          |
| `mac_address`          | str                        | No       | None    | MAC address                           |
| `uptime`               | str                        | No       | None    | Device uptime                         |
| `ha_state`             | str                        | No       | None    | HA state                              |
| `ha_peer_state`        | str                        | No       | None    | HA peer state                         |
| `ha_peer_serial`       | str                        | No       | None    | HA peer serial number                 |
| `available_licenses`   | List[DeviceLicenseModel]   | No       | None    | List of available licenses            |
| `installed_licenses`   | List[DeviceLicenseModel]   | No       | None    | List of installed licenses            |

### Filter Parameters

The `list()` method supports the following filters:

| Parameter       | Type       | Description                                      |
|-----------------|------------|--------------------------------------------------|
| `type`          | str        | Filter by device type (server-side)              |
| `serial_number` | str        | Filter by serial number (server-side)            |
| `model`         | str        | Filter by device model (server/client-side)      |
| `labels`        | List[str]  | Filter by labels (client-side, any match)        |
| `parent`        | str        | Filter by parent (client-side, exact match)      |
| `snippets`      | List[str]  | Filter by snippets (client-side, any match)      |
| `device_only`   | bool       | Filter device-only entries (client-side)         |

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

### Retrieving a Device by ID

```python
# Get a specific device by ID
device = client.device.get("001122334455")
print(f"Device: {device.name}")
print(f"Model: {device.model}")
print(f"Software Version: {device.software_version}")
```

### Fetching a Device by Name

```python
# Fetch a device by its exact name
device = client.device.fetch(name="PA-VM-1")
if device:
    print(f"Found device: {device.name}")
    print(f"Serial: {device.serial_number}")
else:
    print("Device not found")
```

### Listing Devices

```python
# List all devices
all_devices = client.device.list()

for device in all_devices:
    print(device.id, device.name, device.model)
```

### Filtering Responses

```python
# Filter devices by type (server-side)
vm_devices = client.device.list(type="vm")

# Filter devices by serial number (server-side)
specific_device = client.device.list(serial_number="001122334455")

# Filter devices by model (server-side)
pa_devices = client.device.list(model="PA-VM")

# Filter device-only resources (client-side)
device_only = client.device.list(device_only=True)

# Filter by labels (client-side, any match)
labeled_devices = client.device.list(labels=["production", "datacenter-1"])
```

### Controlling Pagination with max_limit

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.device.max_limit = 100

# List all devices - auto-paginates through results
all_devices = client.device.list()

# The devices are fetched in chunks according to the max_limit setting.
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
from scm.client import ScmClient
from scm.exceptions import APIError, ObjectNotPresentError

# Initialize the client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Get all VM firewalls
    vm_firewalls = client.device.list(type="vm")

    print(f"Found {len(vm_firewalls)} VM firewalls:")

    for device in vm_firewalls:
        print(f"ID: {device.id}")
        print(f"Name: {device.name}")
        print(f"Model: {device.model}")
        print(f"Serial: {device.serial_number}")
        print(f"Software Version: {device.software_version}")
        print(f"Connected: {device.is_connected}")

        # Display licenses
        if device.installed_licenses:
            print("Installed licenses:")
            for lic in device.installed_licenses:
                print(f"  - {lic.feature} (expires: {lic.expires})")

        print("---")

    # Get a specific device by ID
    specific_device = client.device.get("001122334455")
    print(f"Retrieved device: {specific_device.name}")

    # Fetch a device by name
    named_device = client.device.fetch(name="PA-VM-1")
    if named_device:
        print(f"Found device by name: {named_device.name}")

except ObjectNotPresentError as e:
    print(f"Device not found: {e}")
except APIError as e:
    print(f"Error retrieving devices: {e}")
```

## Related Models

- [DeviceBaseModel](../../models/setup/device_models.md#Overview)
- [DeviceCreateModel](../../models/setup/device_models.md#Overview)
- [DeviceUpdateModel](../../models/setup/device_models.md#Overview)
- [DeviceResponseModel](../../models/setup/device_models.md#Overview)
- [DeviceLicenseModel](../../models/setup/device_models.md#Overview)
- [DeviceListResponseModel](../../models/setup/device_models.md#Overview)
