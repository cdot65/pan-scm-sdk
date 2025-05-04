# Quarantined Devices

The `QuarantinedDevices` class provides methods to manage quarantined devices in Palo Alto Networks' Strata Cloud Manager.

## Class Definition

```python
class QuarantinedDevices(BaseObject):
    """
    Manages Quarantined Devices in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
    """
```

## Usage

### Initialization

```python
from scm.client import Scm
from scm.config.objects import QuarantinedDevices

# Initialize the API client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize using the unified client approach (recommended)
quarantined_devices_service = client.quarantined_device

# Or initialize using the traditional approach
quarantined_devices_service = QuarantinedDevices(client)
```

## Methods

### create

Creates a new quarantined device.

```python
def create(
    self,
    data: Dict[str, Any],
) -> QuarantinedDevicesResponseModel:
    """
    Creates a new quarantined device.

    Args:
        data: Dictionary containing the quarantined device data

    Returns:
        QuarantinedDevicesResponseModel: The created quarantined device

    Raises:
        InvalidObjectError: If the request payload is invalid
    """
```

#### Example

```python
# Create a new quarantined device
quarantined_device_data = {
    "host_id": "abc123",
    "serial_number": "PA-123456789"
}

# Create the quarantined device
new_device = quarantined_devices_service.create(quarantined_device_data)
print(f"Created quarantined device with host ID: {new_device.host_id}")
```

### list

Lists quarantined devices with optional filtering.

```python
def list(
    self,
    host_id: Optional[str] = None,
    serial_number: Optional[str] = None,
) -> List[QuarantinedDevicesResponseModel]:
    """
    Lists quarantined devices with optional filtering.

    Args:
        host_id: Filter by device host ID
        serial_number: Filter by device serial number

    Returns:
        List[QuarantinedDevicesResponseModel]: A list of quarantined devices matching the filters

    Raises:
        InvalidObjectError: If the response format is invalid
    """
```

#### Example

```python
# List all quarantined devices
all_devices = quarantined_devices_service.list()
print(f"Found {len(all_devices)} quarantined devices")

# List quarantined devices with a specific host ID
filtered_by_host = quarantined_devices_service.list(host_id="abc123")
print(f"Found {len(filtered_by_host)} devices with host ID 'abc123'")

# List quarantined devices with a specific serial number
filtered_by_serial = quarantined_devices_service.list(serial_number="PA-123456789")
print(f"Found {len(filtered_by_serial)} devices with serial number 'PA-123456789'")

# List with both filters applied
filtered_devices = quarantined_devices_service.list(
    host_id="abc123",
    serial_number="PA-123456789"
)
print(f"Found {len(filtered_devices)} devices matching both filters")
```

### delete

Deletes a quarantined device by host ID.

```python
def delete(
    self,
    host_id: str,
) -> None:
    """
    Deletes a quarantined device by host ID.

    Args:
        host_id: The host ID of the quarantined device to delete

    Raises:
        MissingQueryParameterError: If host_id is empty or None
    """
```

#### Example

```python
# Delete a quarantined device by host ID
try:
    quarantined_devices_service.delete("abc123")
    print("Device deleted successfully")
except Exception as e:
    print(f"Error deleting device: {e}")
```

## Complete Example

```python
from scm.client import Scm

# Initialize the unified client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create a new quarantined device
new_device_data = {
    "host_id": "device-12345",
    "serial_number": "PA-987654321"
}

try:
    # Create the device
    new_device = client.quarantined_device.create(new_device_data)
    print(f"Created quarantined device: {new_device.host_id}")

    # List all quarantined devices
    all_devices = client.quarantined_device.list()
    print(f"Total quarantined devices: {len(all_devices)}")

    # List devices with filters
    filtered_devices = client.quarantined_device.list(serial_number="PA-987654321")
    print(f"Found {len(filtered_devices)} devices with specified serial number")

    # Delete the device we just created
    client.quarantined_device.delete(new_device.host_id)
    print(f"Deleted quarantined device: {new_device.host_id}")

    # Verify deletion
    remaining_devices = client.quarantined_device.list(host_id=new_device.host_id)
    print(f"Devices remaining after deletion: {len(remaining_devices)}")

except Exception as e:
    print(f"Error: {e}")
```
