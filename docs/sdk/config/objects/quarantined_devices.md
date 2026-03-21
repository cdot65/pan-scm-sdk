# Quarantined Devices

The `QuarantinedDevices` service manages quarantined device entries in Strata Cloud Manager, supporting create, list, and delete operations for device quarantine management.

## Class Overview

The `QuarantinedDevices` class provides operations for quarantined device entries. It is accessed through the `client.quarantined_device` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the QuarantinedDevices service
quarantined = client.quarantined_device
```

!!! note
    This service does not support `get()`, `update()`, or `fetch()` methods. Quarantined devices are identified by their `host_id` and can be listed with optional filters or deleted by `host_id`.

### Key Attributes

| Attribute       | Type  | Required | Description          |
|-----------------|-------|----------|----------------------|
| `host_id`       | `str` | Yes      | Device host ID       |
| `serial_number` | `str` | No       | Device serial number |

## Methods

### List Quarantined Devices

Retrieves a list of quarantined devices with optional filtering.

```python
# List all quarantined devices
all_devices = client.quarantined_device.list()
print(f"Found {len(all_devices)} quarantined devices")

# Filter by host ID
filtered = client.quarantined_device.list(host_id="abc123")

# Filter by serial number
filtered = client.quarantined_device.list(serial_number="PA-123456789")
```

### Create a Quarantined Device

Creates a new quarantined device entry.

```python
new_device = client.quarantined_device.create({
    "host_id": "device-12345",
    "serial_number": "PA-987654321"
})
print(f"Created device: {new_device.host_id}")
```

### Delete a Quarantined Device

Deletes a quarantined device by host ID.

```python
client.quarantined_device.delete("abc123")
```

## Use Cases

### Device Quarantine Workflow

Quarantine a device, verify the quarantine, then release it.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Quarantine a device
new_device = client.quarantined_device.create({
    "host_id": "device-12345",
    "serial_number": "PA-987654321"
})
print(f"Quarantined device: {new_device.host_id}")

# Verify the quarantine
devices = client.quarantined_device.list(host_id="device-12345")
print(f"Found {len(devices)} matching devices")

# Release the device
client.quarantined_device.delete("device-12345")
print("Device released from quarantine")

# Verify deletion
remaining = client.quarantined_device.list(host_id="device-12345")
print(f"Devices remaining: {len(remaining)}")
```

### Bulk Quarantine Management

List and manage multiple quarantined devices.

```python
# List all quarantined devices
all_devices = client.quarantined_device.list()
for device in all_devices:
    print(f"Host ID: {device.host_id}, Serial: {device.serial_number}")

# Filter by serial number
pa_devices = client.quarantined_device.list(serial_number="PA-987654321")
print(f"Found {len(pa_devices)} devices with specified serial")
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_device = client.quarantined_device.create({
        "host_id": "device-12345",
        "serial_number": "PA-987654321"
    })
except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")

try:
    client.quarantined_device.delete("")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")
```

## Related Topics

- [Quarantined Devices Models](../../models/objects/quarantined_devices_models.md#Overview)
