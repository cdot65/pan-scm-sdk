# Device Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Device models provide a structured way to manage device resources in Palo Alto Networks' Strata Cloud Manager.
These models represent firewall devices, their configuration, licensing, and status information. The models handle
validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `DeviceBaseModel`: Base model with fields common to all device operations
- `DeviceCreateModel`: Model for creating new devices
- `DeviceUpdateModel`: Model for updating existing devices
- `DeviceResponseModel`: Response model for device operations (includes many additional status fields)
- `DeviceLicenseModel`: Model for license entries
- `DeviceListResponseModel`: Model for paginated device list responses

Most models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.
The `DeviceResponseModel` uses `extra="allow"` to accommodate new API fields.

## Model Attributes

### DeviceBaseModel

| Attribute     | Type | Required | Default | Description                        |
|---------------|------|----------|---------|------------------------------------|
| name          | str  | No       | None    | Device name                        |
| display_name  | str  | No       | None    | Display name for the device        |
| serial_number | str  | No       | None    | Device serial number               |
| family        | str  | No       | None    | Device family (e.g., 'vm')         |
| model         | str  | No       | None    | Device model (e.g., 'PA-VM')       |
| folder        | str  | No       | None    | Folder name containing the device  |
| hostname      | str  | No       | None    | Device hostname                    |
| type          | str  | No       | None    | Device type (e.g., 'on-prem')      |
| device_only   | bool | No       | None    | True if device-only entry          |
| is_connected  | bool | No       | None    | Connection status                  |
| description   | str  | No       | None    | Device description                 |

### DeviceCreateModel

Inherits all fields from `DeviceBaseModel` without additional fields.

### DeviceUpdateModel

Extends `DeviceBaseModel` by adding:

| Attribute | Type | Required | Default | Description                              |
|-----------|------|----------|---------|------------------------------------------|
| id        | str  | Yes      | None    | Unique device identifier (serial number) |

### DeviceResponseModel

Extends `DeviceBaseModel` by adding many response-specific fields:

| Attribute               | Type                     | Required | Default | Description                        |
|-------------------------|--------------------------|----------|---------|------------------------------------|
| id                      | str                      | Yes      | None    | Unique device identifier           |
| connected_since         | str                      | No       | None    | ISO timestamp when connected       |
| last_disconnect_time    | str                      | No       | None    | ISO timestamp when disconnected    |
| last_device_update_time | str                      | No       | None    | ISO timestamp of last update       |
| last_das_update_time    | str                      | No       | None    | ISO timestamp of last DAS update   |
| deactivate_wait_hrs     | int                      | No       | None    | Deactivation wait hours            |
| deactivated_by          | str                      | No       | None    | Who deactivated the device         |
| to_be_deactivated_at    | str                      | No       | None    | Scheduled deactivation time        |
| dev_cert_detail         | str                      | No       | None    | Device certificate detail          |
| dev_cert_expiry_date    | str                      | No       | None    | Device certificate expiry          |
| app_version             | str                      | No       | None    | App version                        |
| app_release_date        | str                      | No       | None    | App release date                   |
| av_release_date         | str                      | No       | None    | Antivirus release date             |
| anti_virus_version      | str                      | No       | None    | Antivirus version                  |
| threat_version          | str                      | No       | None    | Threat version                     |
| threat_release_date     | str                      | No       | None    | Threat release date                |
| wf_ver                  | str                      | No       | None    | WildFire version                   |
| wf_release_date         | str                      | No       | None    | WildFire release date              |
| iot_version             | str                      | No       | None    | IoT version                        |
| iot_release_date        | str                      | No       | None    | IoT release date                   |
| gp_client_verion        | str                      | No       | None    | GlobalProtect client version       |
| gp_data_version         | str                      | No       | None    | GlobalProtect data version         |
| log_db_version          | str                      | No       | None    | Log DB version                     |
| software_version        | str                      | No       | None    | Software version                   |
| uptime                  | str                      | No       | None    | Device uptime                      |
| mac_address             | str                      | No       | None    | MAC address                        |
| ip_address              | str                      | No       | None    | IPv4 address                       |
| ipV6_address            | str                      | No       | None    | IPv6 address                       |
| url_db_ver              | str                      | No       | None    | URL DB version                     |
| url_db_type             | str                      | No       | None    | URL DB type                        |
| license_match           | bool                     | No       | None    | License match status               |
| available_licenses      | List[DeviceLicenseModel] | No       | None    | List of available licenses         |
| installed_licenses      | List[DeviceLicenseModel] | No       | None    | List of installed licenses         |
| ha_state                | str                      | No       | None    | HA state                           |
| ha_peer_state           | str                      | No       | None    | HA peer state                      |
| ha_peer_serial          | str                      | No       | None    | HA peer serial number              |
| vm_state                | str                      | No       | None    | VM state                           |

## Supporting Models

### DeviceLicenseModel

| Attribute | Type | Required | Default | Description                              |
|-----------|------|----------|---------|------------------------------------------|
| feature   | str  | Yes      | None    | Feature name for the license             |
| expires   | str  | Yes      | None    | Expiration date (YYYY-MM-DD)             |
| issued    | str  | Yes      | None    | Issued date (YYYY-MM-DD)                 |
| expired   | str  | No       | None    | Whether the license is expired (yes/no)  |
| authcode  | str  | No       | None    | Authorization code for the license       |

### DeviceListResponseModel

| Attribute | Type                     | Required | Default | Description                        |
|-----------|--------------------------|----------|---------|------------------------------------|
| data      | List[DeviceResponseModel] | Yes     | None    | List of device objects             |
| limit     | int                      | Yes      | None    | Max number of devices returned     |
| offset    | int                      | Yes      | None    | Offset for pagination              |
| total     | int                      | Yes      | None    | Total number of devices available  |

## Exceptions

The Device models can raise the following exceptions during validation:

- **ValueError**: Raised when field validation fails
- **ValidationError**: Raised by Pydantic when model validation fails

## Usage Examples

### Listing Devices

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# List all devices
devices = client.device.list()

for device in devices:
    print(f"Device: {device.name}")
    print(f"Model: {device.model}")
    print(f"Serial: {device.serial_number}")
    print(f"Software Version: {device.software_version}")
```

### Getting a Device by ID

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Get device by ID
device = client.device.get("001122334455")
print(f"Device: {device.name}")
print(f"IP Address: {device.ip_address}")
print(f"HA State: {device.ha_state}")
```

### Fetching a Device by Name

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch device by name
device = client.device.fetch(name="PA-VM-1")
if device:
    print(f"Found device: {device.name}")
    print(f"Connected: {device.is_connected}")

    # Access license information
    if device.installed_licenses:
        for lic in device.installed_licenses:
            print(f"License: {lic.feature}")
            print(f"Expires: {lic.expires}")
            print(f"Issued: {lic.issued}")
else:
    print("Device not found")
```

### Filtering Devices

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Filter by type (server-side)
vm_devices = client.device.list(type="vm")

# Filter by model (server-side)
pa_vm_devices = client.device.list(model="PA-VM")

# Filter device-only entries (client-side)
device_only = client.device.list(device_only=True)

for device in vm_devices:
    print(f"VM Device: {device.name} - {device.model}")
```
