# Quarantined Devices Models

## Overview {#Overview}

Quarantined Devices allow you to manage devices that have been quarantined in Palo Alto Networks' Strata Cloud Manager. These models define the structure for creating and retrieving quarantined device configurations.

### Models

The module provides the following Pydantic models:

- `QuarantinedDevicesBaseModel`: Base model with fields common to all quarantined device operations
- `QuarantinedDevicesCreateModel`: Model for creating new quarantined devices
- `QuarantinedDevicesResponseModel`: Response model for quarantined device operations
- `QuarantinedDevicesListParamsModel`: Model for list operation filter parameters

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## QuarantinedDevicesBaseModel

The `QuarantinedDevicesBaseModel` contains fields common to all quarantined device CRUD operations.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| host_id | str | Yes | - | Device host ID |
| serial_number | Optional[str] | No | None | Device serial number |

## QuarantinedDevicesCreateModel

The `QuarantinedDevicesCreateModel` extends the base model for creating new quarantined devices.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| *All attributes from QuarantinedDevicesBaseModel* |  |  |  |  |

## QuarantinedDevicesResponseModel

The `QuarantinedDevicesResponseModel` extends the base model and represents the API response.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| *All attributes from QuarantinedDevicesBaseModel* |  |  |  |  |

## QuarantinedDevicesListParamsModel

The `QuarantinedDevicesListParamsModel` defines parameters for filtering list operations.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| host_id | Optional[str] | No | None | Filter by device host ID |
| serial_number | Optional[str] | No | None | Filter by device serial number |

## Usage Examples

### Creating a Quarantined Device

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
device_data = {
    "host_id": "device-12345",
    "serial_number": "PA-987654321"
}

response = client.quarantined_device.create(device_data)
print(f"Created device: {response.host_id}")
```

### Listing Quarantined Devices with Filters

```python
# List all quarantined devices
all_devices = client.quarantined_device.list()

# List with host_id filter
filtered = client.quarantined_device.list(host_id="device-12345")

# List with serial_number filter
by_serial = client.quarantined_device.list(serial_number="PA-987654321")

# List with both filters
specific = client.quarantined_device.list(
    host_id="device-12345",
    serial_number="PA-987654321"
)
```

### Deleting a Quarantined Device

```python
# Delete by host_id
client.quarantined_device.delete("device-12345")
print("Device deleted successfully")
```

## Best Practices

### Device Management
- Always provide a valid `host_id` when creating quarantined devices
- Use the `serial_number` field when available for better device identification
- Verify device existence before deletion using the `list()` method

### Error Handling
- Handle `InvalidObjectError` for invalid request payloads
- Handle `MissingQueryParameterError` when host_id is missing for delete operations
- Validate `host_id` is not empty before calling `delete()`
