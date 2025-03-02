# Quarantined Devices Models

This document describes the data models used for Quarantined Devices in the Palo Alto Networks Strata Cloud Manager SDK.

## Model Hierarchy

The Quarantined Devices models follow a hierarchical structure:

1. `QuarantinedDevicesBaseModel` - Base model containing common fields
2. `QuarantinedDevicesCreateModel` - Model for creating new quarantined devices
3. `QuarantinedDevicesResponseModel` - Model for API responses
4. `QuarantinedDevicesListParamsModel` - Model for list operation parameters

## QuarantinedDevicesBaseModel

Base model for Quarantined Devices objects containing fields common to all CRUD operations.

```python
class QuarantinedDevicesBaseModel(BaseModel):
    """
    Base model for Quarantined Devices objects containing fields common to all CRUD operations.

    Attributes:
        host_id (str): Device host ID.
        serial_number (Optional[str]): Device serial number.
    """

    # Required fields
    host_id: str = Field(
        ...,
        description="Device host ID",
    )

    # Optional fields
    serial_number: Optional[str] = Field(
        None,
        description="Device serial number",
    )

    # Pydantic model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )
```

### Fields

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `host_id` | str | Yes | Device host ID |
| `serial_number` | Optional[str] | No | Device serial number |

## QuarantinedDevicesCreateModel

Model used for creating new Quarantined Devices.

```python
class QuarantinedDevicesCreateModel(QuarantinedDevicesBaseModel):
    """
    Represents the creation of a new Quarantined Devices object for Palo Alto Networks' Strata Cloud Manager.
    """
```

This model inherits all fields from `QuarantinedDevicesBaseModel`.

### Example Usage

```python
from scm.models.objects import QuarantinedDevicesCreateModel

# Create a minimal instance with required fields
device = QuarantinedDevicesCreateModel(host_id="device-1234")

# Create an instance with all fields
device_with_all_fields = QuarantinedDevicesCreateModel(
    host_id="device-1234",
    serial_number="PA-987654321"
)

# Convert to dictionary for API request
payload = device_with_all_fields.model_dump(exclude_unset=True)
```

## QuarantinedDevicesResponseModel

Model representing the response from the API when creating or retrieving Quarantined Devices.

```python
class QuarantinedDevicesResponseModel(QuarantinedDevicesBaseModel):
    """
    Represents the response from creating or retrieving a Quarantined Devices object
    from Palo Alto Networks' Strata Cloud Manager.
    """
```

This model inherits all fields from `QuarantinedDevicesBaseModel`.

### Example Usage

```python
from scm.models.objects import QuarantinedDevicesResponseModel

# Parse API response into model
api_response = {
    "host_id": "device-1234",
    "serial_number": "PA-987654321"
}

device = QuarantinedDevicesResponseModel(**api_response)
print(f"Host ID: {device.host_id}")
print(f"Serial Number: {device.serial_number}")
```

## QuarantinedDevicesListParamsModel

Model for the parameters used in the list operation to filter Quarantined Devices.

```python
class QuarantinedDevicesListParamsModel(BaseModel):
    """
    Parameters for listing Quarantined Devices.

    Attributes:
        host_id (Optional[str]): Filter by device host ID.
        serial_number (Optional[str]): Filter by device serial number.
    """

    host_id: Optional[str] = Field(
        None,
        description="Filter by device host ID",
    )
    serial_number: Optional[str] = Field(
        None,
        description="Filter by device serial number",
    )
```

### Fields

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `host_id` | Optional[str] | No | Filter by device host ID |
| `serial_number` | Optional[str] | No | Filter by device serial number |

### Example Usage

```python
from scm.models.objects import QuarantinedDevicesListParamsModel

# Create filter parameters model
filter_params = QuarantinedDevicesListParamsModel(
    host_id="device-1234",
    serial_number="PA-987654321"
)

# Convert to dictionary for API request parameters, excluding None values
params = filter_params.model_dump(exclude_none=True)
```