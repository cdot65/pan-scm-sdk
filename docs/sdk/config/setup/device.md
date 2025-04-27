# Device Service (`scm.config.setup.device`)

This page documents the Device service in the SDK configuration layer.

## Overview
The `Device` class provides methods for listing, filtering, and managing device resources in the SCM API. It supports server-side and client-side filtering, pagination, and device-specific operations.

## Main Class
- **Device**: Main entry point for device operations.

## Key Methods
- `list(**filters)`: List devices with optional filters (type, serial_number, model, etc). Supports pagination and both server-side and client-side filtering.
- `_apply_filters(data, filters)`: Internal method to apply client-side filters to a list of devices.

## Filters Supported
- `type`
- `serial_number`
- `model`
- `device_only`

## Example Usage
```python
from scm.config.setup.device import Device
from scm.client import Scm

api_client = Scm(api_key="<your-api-key>")
device_service = Device(api_client)

# List all devices of a specific type
for device in device_service.list(type="vm"):
    print(device.id, device.name)
```

## Related Models
See [DeviceResponseModel](../../models/setup/device_models.md) for the device data structure.

---

For more details, see the source code: [`scm/config/setup/device.py`](../../../scm/config/setup/device.py)
