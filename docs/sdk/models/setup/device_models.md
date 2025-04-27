# Device Models (`scm.models.setup.device`)

This page documents the Pydantic models for Device resources.

## Main Models
- **DeviceResponseModel**: Represents a device resource returned by the SCM API. Includes fields such as `id`, `name`, `serial_number`, `model`, `type`, `available_licenses`, `installed_licenses`, and more.
- **DeviceLicenseModel**: Represents a license associated with a device.
- **DeviceListResponseModel**: Represents a paginated list of devices from the API.

## DeviceResponseModel Fields
- `id`: Unique device identifier (serial number).
- `name`: Device name.
- `serial_number`: Serial number.
- `model`: Device model.
- `type`: Device type (e.g., vm, firewall, panorama).
- `available_licenses`: List of available licenses.
- `installed_licenses`: List of installed licenses.
- ...and many more fields.

## Example Usage
```python
from scm.models.setup.device import DeviceResponseModel

data = {
    "id": "001122334455",
    "name": "PA-VM",
    "serial_number": "001122334455",
    "model": "PA-VM",
    "type": "vm",
    "available_licenses": [],
    "installed_licenses": [],
}
device = DeviceResponseModel.model_validate(data)
print(device.id, device.model)
```

---

For more details, see the source code: [`scm/models/setup/device.py`](../../../scm/models/setup/device.py)
