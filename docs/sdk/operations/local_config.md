# Local Config

Provides access to local device configuration versions and file downloads in Strata Cloud Manager.

## Class Overview

The `LocalConfig` class inherits from `ServiceBase` and provides methods for listing configuration versions and downloading configuration files from devices.

### Methods

| Method | Description | Parameters | Return Type |
| --- | --- | --- | --- |
| `list_versions()` | List config versions for a device | `device` | `List[LocalConfigVersionModel]` |
| `download()` | Download a config file | `device`, `version` | `bytes` |

### Model Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | `int` | Unique identifier for the configuration version entry |
| `serial` | `str` | Device serial number (14-15 digits) |
| `local_version` | `str` | Local configuration version identifier |
| `timestamp` | `datetime` | When the configuration version was created |
| `xfmed_version` | `str` | Transformed configuration version identifier |
| `md5` | `Optional[str]` | MD5 hash of the configuration |

### Exceptions

| Exception | HTTP Code | Description |
| --- | --- | --- |
| `InvalidQueryParameterError` | 400 | Invalid query parameters |
| `MissingQueryParameterError` | 400 | Missing required parameters |
| `AuthenticationError` | 401 | Authentication failed |
| `ObjectNotPresentError` | 404 | Configuration not found |
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

### List Configuration Versions

Retrieve the version history of local configurations for a specified device.

```python
# List all configuration versions for a device
versions = client.local_config.list_versions(device="007951000123456")

for version in versions:
    print(f"Version {version.local_version} at {version.timestamp}")
```

### Download a Configuration File

Download a specific local configuration file as raw XML bytes.

```python
# Download a specific configuration version
config_bytes = client.local_config.download(
    device="007951000123456",
    version="1"
)

# Save to a file
with open("device-config.xml", "wb") as f:
    f.write(config_bytes)

print(f"Downloaded {len(config_bytes)} bytes")
```

## Use Cases

### Back Up Device Configuration

```python
# Get all versions, then download the latest
versions = client.local_config.list_versions(device="007951000123456")

if versions:
    latest = versions[0]
    config = client.local_config.download(
        device="007951000123456",
        version=str(latest.id)
    )
    filename = f"backup-{latest.serial}-{latest.local_version}.xml"
    with open(filename, "wb") as f:
        f.write(config)
    print(f"Backed up to {filename}")
else:
    print("No configuration versions found")
```

### Track Configuration Changes

```python
# Monitor configuration version history
versions = client.local_config.list_versions(device="007951000123456")

for v in versions:
    print(f"ID: {v.id} | Version: {v.local_version} | "
          f"Transformed: {v.xfmed_version} | Time: {v.timestamp}")
```

## Error Handling

```python
from scm.exceptions import (
    AuthenticationError,
    ObjectNotPresentError,
    ServerError,
)

try:
    versions = client.local_config.list_versions(device="007951000123456")
except AuthenticationError:
    print("Authentication failed. Check your credentials.")
except ObjectNotPresentError:
    print("Device not found.")
except ServerError as e:
    print(f"Server error: {e.message}")
```

## Related Topics

- [Operations Models](../../models/operations/index.md)
- [Device Operations](device_operations.md)
- [Client Module](../../client.md)
