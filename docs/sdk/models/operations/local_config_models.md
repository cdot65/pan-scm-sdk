# Local Config Models

Pydantic models for local device configuration version data in Strata Cloud Manager.

## Overview

The Local Config models represent configuration version entries retrieved from devices. These models handle:

- Configuration version metadata (version identifiers, timestamps)
- Device serial number associations
- Transformation tracking between original and processed configurations

## Models

### LocalConfigVersionModel

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `id` | `int` | Yes | - | Unique identifier for the configuration version entry |
| `serial` | `str` | Yes | - | Device serial number (14-15 digits) |
| `local_version` | `str` | Yes | - | Local configuration version identifier |
| `timestamp` | `datetime` | Yes | - | When the configuration version was created |
| `xfmed_version` | `str` | Yes | - | Transformed configuration version identifier |
| `md5` | `Optional[str]` | No | `None` | MD5 hash of the configuration |

## Usage Examples

### Parsing Version Data

```python
from scm.models.operations.local_config import LocalConfigVersionModel

# Parse a version entry from API response
version = LocalConfigVersionModel(
    id=1,
    serial="007951000123456",
    local_version="1.0.0",
    timestamp="2025-01-15T10:30:00Z",
    xfmed_version="1.0.0-transformed"
)

print(f"Version: {version.local_version}")
print(f"Device: {version.serial}")
print(f"Timestamp: {version.timestamp}")
```

## Related Documentation

- [Local Config Service](../../operations/local_config.md)
- [Operations Models Overview](index.md)
