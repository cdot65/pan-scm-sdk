# Device Operations Models

Pydantic models for device operation job dispatch and status tracking in Strata Cloud Manager.

## Overview

The Device Operations models handle validation and serialization for asynchronous device jobs. These models cover:

- Device serial number validation for job dispatch
- Job creation responses with job identifiers
- Job status tracking with progress and state information
- Per-device results with command execution details

## Request Models

### DeviceOperationsRequestModel

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `devices` | `List[str]` | Yes | 1-5 device serial numbers (14-15 digits each) |

**Validation Rules:**

- Minimum 1 device, maximum 5 devices
- Each serial number must match pattern `^\d{14,15}$`

## Response Models

### JobCreatedModel

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `job_id` | `str` | Yes | Unique identifier for the created job |

### DeviceJobStatusModel

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `jobId` | `str` | Yes | Unique identifier for the job |
| `progress` | `int` | Yes | Job completion percentage (0-100) |
| `state` | `str` | Yes | Current state: `pending`, `in_progress`, `complete`, `failed` |
| `request` | `DeviceJobRequestModel` | Yes | Original request details |
| `results` | `List[DeviceJobResultModel]` | No | Results from each device |

### DeviceJobResultModel

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `device` | `str` | Yes | Device serial number |
| `state` | `str` | Yes | Job state for this device |
| `created_ts` | `str` | Yes | Job creation timestamp |
| `updated_ts` | `str` | Yes | Last update timestamp |
| `details` | `DeviceJobDetailsModel` | Yes | Command execution results |

### DeviceJobDetailsModel

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `msg` | `str` | Yes | - | Status message from command execution |
| `result` | `Dict[str, Any]` | No | `{}` | Result data (structure varies by command type) |

### DeviceJobRequestModel

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `command` | `str` | Yes | The command that was executed |
| `devices` | `List[str]` | Yes | Device serial numbers |

## Usage Examples

### Validating Device Input

```python
from scm.models.operations.device_operations import DeviceOperationsRequestModel
from pydantic import ValidationError

# Valid request
request = DeviceOperationsRequestModel(
    devices=["007951000123456", "007951000123457"]
)

# Invalid - too many devices
try:
    request = DeviceOperationsRequestModel(
        devices=["00795100012345" + str(i) for i in range(6)]
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Parsing Job Status

```python
from scm.models.operations.device_operations import DeviceJobStatusModel

status = DeviceJobStatusModel(**api_response)
print(f"Job: {status.jobId}")
print(f"Progress: {status.progress}%")
print(f"State: {status.state}")

for result in status.results:
    print(f"  Device {result.device}: {result.details.msg}")
```

## Related Documentation

- [Device Operations Service](../../operations/device_operations.md)
- [Operations Models Overview](index.md)
