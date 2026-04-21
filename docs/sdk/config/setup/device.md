# Device Configuration Object

Provides access to device resources in Palo Alto Networks Strata Cloud Manager. Devices enroll out-of-band, so the SDK does not expose create or delete — but it does expose `update()` to modify the five writable fields defined by the upstream `devices-put` schema (`display_name`, `folder`, `description`, `labels`, `snippets`).

## Class Overview

The `Device` class supports listing, filtering, retrieving, and updating device resources.

### Methods

| Method     | Description                   | Parameters                 | Return Type                 |
|------------|-------------------------------|----------------------------|-----------------------------|
| `get()`    | Retrieves a device by ID      | `device_id: str`           | `DeviceResponseModel`       |
| `fetch()`  | Gets device by name           | `name: str`                | `DeviceResponseModel`       |
| `list()`   | Lists devices with filtering  | `**filters`                | `List[DeviceResponseModel]` |
| `update()` | Updates a device's metadata   | `device: DeviceUpdateModel` | `DeviceResponseModel`       |

### Model Attributes

| Attribute       | Type       | Required | Default | Description                       |
|-----------------|------------|----------|---------|-----------------------------------|
| `name`          | str        | No       | None    | Device name                       |
| `id`            | str        | Yes*     | None    | Unique device identifier          |
| `display_name`  | str        | No       | None    | Display name for the device       |
| `serial_number` | str        | No       | None    | Device serial number              |
| `family`        | str        | No       | None    | Device family (e.g., 'vm')        |
| `model`         | str        | No       | None    | Device model (e.g., 'PA-VM')      |
| `folder`        | str        | No       | None    | Folder name containing the device |
| `hostname`      | str        | No       | None    | Device hostname                   |
| `type`          | str        | No       | None    | Device type (e.g., 'on-prem')     |
| `device_only`   | bool       | No       | None    | True if device-only entry         |
| `is_connected`  | bool       | No       | None    | Connection status                 |
| `description`   | str        | No       | None    | Device description                |
| `labels`        | List[str]  | No       | None    | Labels assigned to the device     |
| `snippets`      | List[str]  | No       | None    | Snippets associated with the device |

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

### Update a Device

The upstream `PUT /config/setup/v1/devices/{id}` endpoint accepts only five writable fields: `display_name`, `folder`, `description`, `labels`, and `snippets`. Pass a `DeviceUpdateModel` with the device's `id` plus any subset of those fields.

```python
from scm.models.setup.device import DeviceUpdateModel

# Attach labels to a device
updated = client.device.update(
    DeviceUpdateModel(
        id="001122334455",
        labels=["production", "datacenter-1"],
    )
)

# Move a device into a different folder and rename it
updated = client.device.update(
    DeviceUpdateModel(
        id="001122334455",
        folder="Prod",
        display_name="edge-fw-1",
        description="Edge firewall, east region",
    )
)
```

Fields not listed in `DeviceUpdateModel` (e.g. `serial_number`, `hostname`, `is_connected`) are not accepted by the API and will raise a validation error at the SDK layer.

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
