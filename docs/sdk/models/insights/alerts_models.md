# Alert Models

## Overview

The Alert models provide structured representations of security and operational alerts from the Prisma Access Insights API. These models handle data validation, field mapping, and type safety for alert-related operations.

## Model Classes

### Alert

The main alert model representing individual security or operational alerts.

#### Attributes

| Attribute             | Type                     | Required | Description                                                     |
|-----------------------|--------------------------|----------|-----------------------------------------------------------------|
| id                    | str                      | Yes      | Unique alert identifier (mapped from `alert_id`)               |
| name                  | Optional[str]            | No       | Alert message/description (mapped from `message`)              |
| severity              | Optional[str]            | No       | Alert severity level (see AlertSeverity constants)             |
| severity_id           | Optional[int]            | No       | Numeric severity identifier                                     |
| status                | Optional[str]            | No       | Current alert state (mapped from `state`, see AlertStatus)     |
| timestamp             | Optional[str]            | No       | When alert was raised (mapped from `raised_time`)              |
| updated_time          | Optional[str]            | No       | Last update timestamp                                           |
| description           | Optional[str]            | No       | Detailed alert description                                      |
| folder                | Optional[str]            | No       | Associated folder location                                      |
| source                | Optional[str]            | No       | Source system that generated the alert                         |
| category              | Optional[str]            | No       | Alert category (e.g., "Remote Networks", "GlobalProtect")      |
| code                  | Optional[str]            | No       | Internal alert code                                             |
| impacted_resources    | Optional[List[str]]      | No       | List of affected resources (mapped from `primary_impacted_objects`) |
| metadata              | Optional[Dict[str, Any]] | No       | Additional context data (mapped from `resource_context`)       |
| clear_reason          | Optional[str]            | No       | Reason the alert was cleared (if applicable)                   |
| age                   | Optional[int]            | No       | Alert age in days                                              |

#### Field Mapping

The Alert model uses Pydantic field aliases to map API field names to more intuitive property names:

```python
# API field -> Model property
alert_id -> id
message -> name
state -> status
raised_time -> timestamp
primary_impacted_objects -> impacted_resources
resource_context -> metadata
```

#### JSON Field Handling

The `impacted_resources` and `metadata` fields include automatic JSON parsing:

```python
@field_validator("impacted_resources", "metadata", mode="before")
def parse_json_string(cls, v):
    """Parse JSON string fields if needed."""
    if isinstance(v, str):
        import json
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v
```

### AlertStatistic

Model for aggregated alert statistics returned by statistical queries.

#### Attributes

| Attribute    | Type          | Required | Description                          |
|--------------|---------------|----------|--------------------------------------|
| severity     | Optional[str] | No       | Severity level for grouped data      |
| severity_id  | Optional[int] | No       | Numeric severity identifier          |
| category     | Optional[str] | No       | Category for grouped data            |
| state        | Optional[str] | No       | Alert state for grouped data         |
| count        | Optional[int] | No       | Count of alerts in this group        |

The model uses `ConfigDict(extra="allow")` to accept additional fields that might be returned by the API.

### AlertSeverity

Constants class providing standard alert severity levels.

```python
class AlertSeverity:
    """Alert severity levels - Note: API returns capitalized values."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"
    NOTIFICATION = "Notification"
```

### AlertStatus

Constants class providing standard alert status values.

```python
class AlertStatus:
    """Alert status values."""

    RAISED = "Raised"
    RAISED_CHILD = "RaisedChild"
    CLEARED = "Cleared"
```

## Usage Examples

### Working with Alert Objects

```python
from scm.models.insights.alerts import Alert, AlertSeverity, AlertStatus

# Alert data from API
alert_data = {
    "alert_id": "123e4567-e89b-12d3-a456-426614174000",
    "message": "High CPU utilization detected",
    "severity": "High",
    "state": "Raised",
    "raised_time": "2024-01-20T10:30:00Z",
    "category": "System",
    "primary_impacted_objects": ["gateway-1", "gateway-2"]
}

# Create Alert model instance
alert = Alert(**alert_data)

# Access properties with friendly names
print(f"Alert ID: {alert.id}")
print(f"Message: {alert.name}")
print(f"Severity: {alert.severity}")
print(f"Status: {alert.status}")
print(f"Raised at: {alert.timestamp}")
print(f"Impacted: {', '.join(alert.impacted_resources)}")

# Check severity level
if alert.severity == AlertSeverity.HIGH:
    print("This is a high severity alert!")

# Check status
if alert.status == AlertStatus.RAISED:
    print("Alert is currently active")
```

### Working with Statistics

```python
from scm.models.insights.alerts import AlertStatistic

# Statistics data from API
stat_data = {
    "severity": "Critical",
    "count": 15,
    "additional_field": "extra_data"  # Will be preserved due to extra="allow"
}

# Create statistic model
stat = AlertStatistic(**stat_data)

print(f"Severity: {stat.severity}")
print(f"Count: {stat.count}")
```

### JSON Field Parsing

```python
# Alert with JSON string fields
alert_data_with_json = {
    "alert_id": "test-123",
    "message": "Test alert",
    "primary_impacted_objects": '["server1", "server2"]',  # JSON string
    "resource_context": '{"region": "us-west", "zone": "1a"}'  # JSON string
}

# Model automatically parses JSON strings
alert = Alert(**alert_data_with_json)

# Access parsed data
print(alert.impacted_resources)  # ['server1', 'server2']
print(alert.metadata)  # {'region': 'us-west', 'zone': '1a'}
```

### Model Validation

```python
from pydantic import ValidationError

try:
    # Invalid data - missing required field
    alert = Alert(name="Test")  # Missing 'id' field
except ValidationError as e:
    print(f"Validation error: {e}")

# Valid minimal alert
minimal_alert = Alert(
    id="test-123",
    name="Test Alert"
)
```

## Integration with Alerts Service

These models are used throughout the Alerts service:

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# List returns List[Alert]
alerts = client.insights.alerts.list(severity=["high", "critical"])
for alert in alerts:
    # 'alert' is an Alert model instance
    print(f"{alert.name}: {alert.severity}")

# Statistics return List[AlertStatistic]
stats = client.insights.alerts.get_statistics()
for stat in stats:
    # 'stat' is an AlertStatistic model instance
    print(f"{stat.severity}: {stat.count} alerts")
```

## Best Practices

1. **Use Constants**: Always use `AlertSeverity` and `AlertStatus` constants for comparisons
2. **Handle Optional Fields**: Check for None before using optional fields
3. **Type Hints**: Use the models in type hints for better IDE support
4. **Field Access**: Use model properties rather than dictionary access
5. **JSON Fields**: Be aware that `impacted_resources` and `metadata` are automatically parsed

## Related Documentation

- [Alerts Service](../../config/insights/alerts.md) - Service methods using these models
- [Insights Overview](index.md) - Overview of all Insights models
