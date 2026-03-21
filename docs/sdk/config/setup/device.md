# Device Configuration Object

Provides read-only access to device resources for listing, filtering, and retrieving devices in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `Device` class provides methods for listing, filtering, and retrieving device resources. This is a read-only resource supporting get, fetch, and list operations.

### Methods

| Method    | Description                  | Parameters         | Return Type                 |
|-----------|------------------------------|--------------------|-----------------------------|
| `get()`   | Retrieves a device by ID    | `device_id: str`   | `DeviceResponseModel`       |
| `fetch()` | Gets device by name         | `name: str`        | `DeviceResponseModel`       |
| `list()`  | Lists devices with filtering | `**filters`        | `List[DeviceResponseModel]` |

### Model Attributes

| Attribute       | Type | Required | Default | Description                       |
|-----------------|------|----------|---------|-----------------------------------|
| `name`          | str  | No       | None    | Device name                       |
| `id`            | str  | Yes*     | None    | Unique device identifier          |
| `display_name`  | str  | No       | None    | Display name for the device       |
| `serial_number` | str  | No       | None    | Device serial number              |
| `family`        | str  | No       | None    | Device family (e.g., 'vm')        |
| `model`         | str  | No       | None    | Device model (e.g., 'PA-VM')      |
| `folder`        | str  | No       | None    | Folder name containing the device |
| `hostname`      | str  | No       | None    | Device hostname                   |
| `type`          | str  | No       | None    | Device type (e.g., 'on-prem')     |
| `device_only`   | bool | No       | None    | True if device-only entry         |
| `is_connected`  | bool | No       | None    | Connection status                 |
| `description`   | str  | No       | None    | Device description                |

\* Only required for response models

#### Response-Only Attributes

| Attribute            | Type                     | Required | Default | Description              |
|----------------------|--------------------------|----------|---------|--------------------------|
| `connected_since`    | str                      | No       | None    | ISO timestamp when connected |
| `software_version`   | str                      | No       | None    | Software version         |
| `ip_address`         | str                      | No       | None    | IPv4 address             |
| `ipV6_address`       | str                      | No       | None    | IPv6 address             |
| `mac_address`        | str                      | No       | None    | MAC address              |
| `uptime`             | str                      | No       | None    | Device uptime            |
| `ha_state`           | str                      | No       | None    | HA state                 |
| `ha_peer_state`      | str                      | No       | None    | HA peer state            |
| `ha_peer_serial`     | str                      | No       | None    | HA peer serial number    |
| `available_licenses` | List[DeviceLicenseModel] | No       | None    | Available licenses       |
| `installed_licenses` | List[DeviceLicenseModel] | No       | None    | Installed licenses       |

### Exceptions

| Exception              | HTTP Code | Description                   |
|------------------------|-----------|-------------------------------|
| `InvalidObjectError`   | 400       | Invalid device data or format |
| `ObjectNotPresentError`| 404       | Requested device not found    |
| `APIError`             | Various   | General API communication error |
| `AuthenticationError`  | 401       | Authentication failed         |
| `ServerError`          | 500       | Internal server error         |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

devices = client.device
```

## Methods

### List Devices

```python
all_devices = client.device.list()

for device in all_devices:
    print(device.id, device.name, device.model)
```

**Filtering responses:**

```python
# Filter by type (server-side)
vm_devices = client.device.list(type="vm")

# Filter by serial number (server-side)
specific_device = client.device.list(serial_number="001122334455")

# Filter by model (server-side)
pa_devices = client.device.list(model="PA-VM")

# Filter device-only resources (client-side)
device_only = client.device.list(device_only=True)

# Filter by labels (client-side, any match)
labeled_devices = client.device.list(labels=["production", "datacenter-1"])
```

**Controlling pagination with max_limit:**

```python
client.device.max_limit = 100

all_devices = client.device.list()
```

### Fetch a Device

```python
device = client.device.fetch(name="PA-VM-1")
if device:
    print(f"Found device: {device.name}")
    print(f"Serial: {device.serial_number}")
```

### Get a Device by ID

```python
device = client.device.get("001122334455")
print(f"Device: {device.name}")
print(f"Model: {device.model}")
print(f"Software Version: {device.software_version}")
```

## Error Handling

```python
from scm.exceptions import ObjectNotPresentError, InvalidObjectError, APIError

try:
    device = client.device.get("nonexistent-id")
except ObjectNotPresentError as e:
    print(f"Device not found: {e}")
except InvalidObjectError as e:
    print(f"Invalid device type: {e}")
except APIError as e:
    print(f"API error occurred: {e}")
```

## Related Topics

- [Device Models](../../models/setup/device_models.md#Overview)
- [Setup Overview](index.md)
- [API Client](../../client.md)
