# Device Models

## Table of Contents

1. [Overview](#overview)
2. [Models](#models)
    - [DeviceLicenseModel](#devicelicensemodel)
    - [DeviceResponseModel](#deviceresponsemodel)
    - [DeviceListResponseModel](#devicelistresponsemodel)
3. [Model Validation Rules](#model-validation-rules)
4. [Usage Examples](#usage-examples)
    - [Creating Model Instances](#creating-model-instances)
    - [Model Validation](#model-validation)
    - [Model Serialization](#model-serialization)
    - [API Integration Examples](#api-integration-examples)

## Overview

This page documents the Pydantic models used for device operations in the Strata Cloud Manager SDK. These models provide structured data validation and serialization for device data returned by the API.

## Models

### DeviceLicenseModel

Model representing a license associated with a device.

```python
class DeviceLicenseModel(BaseModel):
    name: str
    description: Optional[str] = None
    expiry: Optional[str] = None
    feature: Optional[str] = None
```

### DeviceResponseModel

Model for device responses from the API.

```python
class DeviceResponseModel(BaseModel):
    id: str
    name: str
    serial_number: str
    model: str
    type: str
    available_licenses: Optional[List[DeviceLicenseModel]] = None
    installed_licenses: Optional[List[DeviceLicenseModel]] = None
    # Additional fields omitted for brevity
```

### DeviceListResponseModel

Model for a paginated list of devices from the API.

```python
class DeviceListResponseModel(BaseModel):
    items: List[DeviceResponseModel]
    count: int
    total: int
    next_cursor: Optional[str] = None
```

## Model Validation Rules

| Field              | Validation Rules                                        |
|--------------------|--------------------------------------------------------|
| `id`               | String, typically matches the serial_number             |
| `name`             | Non-empty string                                        |
| `serial_number`    | String, device unique identifier                        |
| `model`            | String, device model identifier (e.g., "PA-VM")         |
| `type`             | String, device type (e.g., "vm", "firewall", "panorama")|
| `available_licenses`| Optional list of DeviceLicenseModel objects            |
| `installed_licenses`| Optional list of DeviceLicenseModel objects            |

The DeviceLicenseModel includes validations for:
- `name`: Required string field for license name
- `description`: Optional string description
- `expiry`: Optional ISO8601 timestamp string
- `feature`: Optional string indicating the feature covered by the license

## Usage Examples

### Creating Model Instances

```python
from scm.models.setup.device import DeviceResponseModel, DeviceLicenseModel

# Create a license model
license_model = DeviceLicenseModel(
    name="VM-300",
    description="VM-Series Firewall License",
    expiry="2025-12-31T23:59:59Z",
    feature="Firewall"
)

# Create a device model
device = DeviceResponseModel(
    id="001122334455",
    name="PA-VM-1",
    serial_number="001122334455",
    model="PA-VM",
    type="vm",
    available_licenses=[],
    installed_licenses=[license_model]
)
```

### Model Validation

```python
from pydantic_core import ValidationError
from scm.models.setup.device import DeviceResponseModel

try:
    # Missing required fields
    DeviceResponseModel(id="001122334455")
except ValidationError as e:
    print("Validation error:", e)
```

### Model Serialization

```python
device = DeviceResponseModel(
    id="001122334455",
    name="PA-VM-1",
    serial_number="001122334455",
    model="PA-VM",
    type="vm"
)
# Convert to dict
device_dict = device.model_dump()
# Convert to JSON
device_json = device.model_dump_json()
```

### API Integration Examples

```python
from scm.config.setup.device import Device
from scm.client import Scm

# Initialize client and service
client = Scm(api_key="your-api-key")
devices = Device(client)

# List devices
device_list = devices.list(type="vm")

# Work with device data
for device in device_list:
    print(f"Device: {device.name} ({device.model})")
    
    # Access license information
    if device.installed_licenses:
        for license in device.installed_licenses:
            print(f"  License: {license.name}")
            if license.expiry:
                print(f"  Expires: {license.expiry}")
```