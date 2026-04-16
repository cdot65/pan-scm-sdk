# Device Operations

Dispatch and monitor asynchronous device operation jobs in Strata Cloud Manager.

## Class Overview

The `DeviceOperations` class inherits from `ServiceBase` and provides methods for dispatching asynchronous jobs to retrieve operational data from devices. Each method supports both async (fire-and-forget) and sync (poll-to-completion) modes.

### Methods

| Method | Description | Parameters | Return Type |
| --- | --- | --- | --- |
| `route_table()` | Retrieve route table | `devices`, `sync`, `poll_interval`, `timeout` | `JobCreatedModel` or `DeviceJobStatusModel` |
| `fib_table()` | Retrieve FIB table | `devices`, `sync`, `poll_interval`, `timeout` | `JobCreatedModel` or `DeviceJobStatusModel` |
| `dns_proxy()` | Retrieve DNS proxy table | `devices`, `sync`, `poll_interval`, `timeout` | `JobCreatedModel` or `DeviceJobStatusModel` |
| `device_interfaces()` | Retrieve network interfaces | `devices`, `sync`, `poll_interval`, `timeout` | `JobCreatedModel` or `DeviceJobStatusModel` |
| `device_rules()` | Retrieve rules | `devices`, `sync`, `poll_interval`, `timeout` | `JobCreatedModel` or `DeviceJobStatusModel` |
| `bgp_policy_export()` | BGP policy export | `devices`, `sync`, `poll_interval`, `timeout` | `JobCreatedModel` or `DeviceJobStatusModel` |
| `logging_service_status()` | Logging service status | `devices`, `sync`, `poll_interval`, `timeout` | `JobCreatedModel` or `DeviceJobStatusModel` |
| `get_job_status()` | Poll job status | `job_id` | `DeviceJobStatusModel` |

### Common Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `devices` | `List[str]` | Yes | - | 1-5 device serial numbers (14-15 digits each) |
| `sync` | `bool` | No | `False` | If `True`, poll until job completes or times out |
| `poll_interval` | `int` | No | `10` | Seconds between polls when `sync=True` |
| `timeout` | `int` | No | `300` | Max seconds to wait when `sync=True` |

### Exceptions

| Exception | HTTP Code | Description |
| --- | --- | --- |
| `ValidationError` | - | Invalid device list (empty, >5, or bad serial format) |
| `JobTimeoutError` | - | Job did not complete within timeout (sync mode) |
| `AuthenticationError` | 401 | Authentication failed |
| `ServerError` | 500 | Internal server error |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)
```

## Methods

### Async Mode (Default)

Dispatch a job and receive a job ID immediately for manual polling.

```python
# Dispatch a route table retrieval job
job = client.device_operations.route_table(
    devices=["007951000123456"]
)
print(f"Job dispatched: {job.job_id}")

# Poll for results manually
status = client.device_operations.get_job_status(job.job_id)
print(f"State: {status.state}, Progress: {status.progress}%")
```

### Sync Mode

Dispatch a job and wait for it to complete before returning.

```python
# Dispatch and wait for completion
result = client.device_operations.route_table(
    devices=["007951000123456"],
    sync=True,
    poll_interval=5,
    timeout=120
)

print(f"Job state: {result.state}")
for device_result in result.results:
    print(f"Device {device_result.device}: {device_result.details.msg}")
```

### Retrieve Route Table

```python
result = client.device_operations.route_table(
    devices=["007951000123456", "007951000123457"],
    sync=True
)

for device_result in result.results:
    routes = device_result.details.result
    print(f"Routes for {device_result.device}: {routes}")
```

### Retrieve FIB Table

```python
result = client.device_operations.fib_table(
    devices=["007951000123456"],
    sync=True
)
```

### Retrieve Network Interfaces

```python
result = client.device_operations.device_interfaces(
    devices=["007951000123456"],
    sync=True
)
```

### Retrieve Device Rules

```python
result = client.device_operations.device_rules(
    devices=["007951000123456"],
    sync=True
)
```

### BGP Policy Export

```python
result = client.device_operations.bgp_policy_export(
    devices=["007951000123456"],
    sync=True
)
```

### Logging Service Status

```python
result = client.device_operations.logging_service_status(
    devices=["007951000123456"],
    sync=True
)
```

### DNS Proxy

```python
result = client.device_operations.dns_proxy(
    devices=["007951000123456"],
    sync=True
)
```

## Use Cases

### Multi-Device Route Audit

```python
devices = [
    "007951000123456",
    "007951000123457",
    "007951000123458",
]

result = client.device_operations.route_table(
    devices=devices,
    sync=True,
    timeout=120
)

for device_result in result.results:
    if device_result.state == "complete":
        print(f"\nRoutes for {device_result.device}:")
        for vrf, routes in device_result.details.result.items():
            print(f"  VRF {vrf}: {len(routes)} routes")
    else:
        print(f"Device {device_result.device}: {device_result.state}")
```

### Async Job Monitoring

```python
import time

# Dispatch multiple jobs
jobs = []
for device in ["007951000123456", "007951000123457"]:
    job = client.device_operations.route_table(devices=[device])
    jobs.append(job)
    print(f"Dispatched job {job.job_id} for {device}")

# Poll all jobs
for job in jobs:
    while True:
        status = client.device_operations.get_job_status(job.job_id)
        if status.state in ("complete", "failed"):
            print(f"Job {job.job_id}: {status.state}")
            break
        time.sleep(5)
```

## Error Handling

```python
from pydantic import ValidationError
from scm.exceptions import (
    AuthenticationError,
    JobTimeoutError,
    ServerError,
)

try:
    result = client.device_operations.route_table(
        devices=["007951000123456"],
        sync=True,
        timeout=60
    )
except ValidationError as e:
    print(f"Invalid device list: {e}")
except JobTimeoutError as e:
    print(f"Job {e.job_id} timed out (last state: {e.last_state})")
    # Can resume polling manually
    status = client.device_operations.get_job_status(e.job_id)
except AuthenticationError:
    print("Authentication failed. Check your credentials.")
except ServerError as e:
    print(f"Server error: {e.message}")
```

## Related Topics

- [Operations Models](../../models/operations/index.md)
- [Local Config](local_config.md)
- [Client Module](../../client.md)
- [Exceptions](../../exceptions.md)
