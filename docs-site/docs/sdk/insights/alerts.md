# Alerts Configuration Object

Provides access to security and operational alerts from the Prisma Access Insights API in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `Alerts` class inherits from `InsightsBaseObject` and provides methods for retrieving alerts, generating statistics, and creating timeline views of alert activity.

### Methods

| Method             | Description                  | Parameters                                                       | Return Type            |
|--------------------|------------------------------|------------------------------------------------------------------|------------------------|
| `list()`           | Lists alerts with filtering  | `severity`, `status`, `start_time`, `end_time`, `category`, etc. | `List[Alert]`          |
| `query()`          | Execute custom query         | `properties`, `filter`, `group_by`, `order_by`, etc.             | `InsightsResponse`     |
| `get_statistics()` | Get alert statistics         | `time_range`, `group_by`, `exclude_notifications`                | `List[AlertStatistic]` |
| `get_timeline()`   | Get alert timeline/histogram | `time_range`, `interval`, `status`, `exclude_notifications`      | `List[AlertStatistic]` |

### Model Attributes

| Attribute            | Type                     | Description                                                 |
|----------------------|--------------------------|-------------------------------------------------------------|
| `id`                 | str                      | Alert ID (mapped from `alert_id`)                           |
| `name`               | Optional[str]            | Alert message/name (mapped from `message`)                  |
| `severity`           | Optional[str]            | Alert severity (Critical, High, Medium, Low, etc.)          |
| `severity_id`        | Optional[int]            | Numeric severity identifier                                 |
| `status`             | Optional[str]            | Alert state (Raised, RaisedChild, Cleared)                  |
| `timestamp`          | Optional[str]            | When alert was raised (mapped from `raised_time`)           |
| `updated_time`       | Optional[str]            | Last update timestamp                                       |
| `description`        | Optional[str]            | Detailed alert description                                  |
| `folder`             | Optional[str]            | Associated folder                                           |
| `source`             | Optional[str]            | Alert source                                                |
| `category`           | Optional[str]            | Alert category                                              |
| `code`               | Optional[str]            | Alert code                                                  |
| `impacted_resources` | Optional[List[str]]      | Affected resources (mapped from `primary_impacted_objects`) |
| `metadata`           | Optional[Dict[str, Any]] | Additional context (mapped from `resource_context`)         |
| `clear_reason`       | Optional[str]            | Reason alert was cleared                                    |
| `age`                | Optional[int]            | Alert age in days                                           |

### Exceptions

| Exception                    | HTTP Code | Description                 |
|------------------------------|-----------|-----------------------------|
| `InvalidObjectError`         | 400       | Invalid query parameters    |
| `MissingQueryParameterError` | 400       | Missing required parameters |
| `AuthenticationError`        | 401       | Authentication failed       |
| `ServerError`                | 500       | Internal server error       |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

alerts = client.insights.alerts
```

## Methods

### List Alerts

```python
# List all alerts (default: last 30 days)
all_alerts = client.insights.alerts.list()
print(f"Found {len(all_alerts)} alerts")

# List alerts with specific severity
critical_alerts = client.insights.alerts.list(
    severity=["critical", "high"]
)

# List alerts from the last 7 days
recent_alerts = client.insights.alerts.list(start_time=7)
```

**Filtering responses:**

```python
filtered_alerts = client.insights.alerts.list(
    severity=["high", "critical"],
    status=["Raised"],
    category="Remote Networks",
    start_time=30,
    max_results=100
)

for alert in filtered_alerts:
    print(f"Alert: {alert.name}")
    print(f"  Severity: {alert.severity}")
    print(f"  Status: {alert.status}")
    print(f"  Category: {alert.category}")
```

### Get Alert Statistics

```python
# Get statistics grouped by severity (default)
severity_stats = client.insights.alerts.get_statistics()
for stat in severity_stats:
    print(f"Severity: {stat.severity}, Count: {stat.count}")

# Get statistics grouped by category
category_stats = client.insights.alerts.get_statistics(
    time_range=90,
    group_by="category",
    exclude_notifications=True
)

# Get statistics grouped by state
state_stats = client.insights.alerts.get_statistics(
    time_range=30,
    group_by="state"
)
```

### Get Alert Timeline

```python
# Get hourly timeline for the last 7 days
hourly_timeline = client.insights.alerts.get_timeline(
    time_range=7,
    interval="hour",
    status="Raised"
)
for point in hourly_timeline:
    print(f"Time: {point.state}, Count: {point.count}")

# Get daily timeline for the last 30 days
daily_timeline = client.insights.alerts.get_timeline(
    time_range=30,
    interval="day",
    status="Raised",
    exclude_notifications=True
)

# Get weekly timeline
weekly_timeline = client.insights.alerts.get_timeline(
    time_range=90,
    interval="week",
    status="Cleared"
)
```

### Execute Custom Query

```python
# Custom query with specific properties and filters
custom_query = client.insights.alerts.query(
    properties=[
        {"property": "alert_id"},
        {"property": "message"},
        {"property": "severity"},
        {"property": "state"},
        {"property": "raised_time"}
    ],
    filter={
        "rules": [
            {"property": "severity", "operator": "in", "values": ["Critical", "High"]},
            {"property": "state", "operator": "equals", "values": ["Raised"]},
            {"property": "updated_time", "operator": "last_n_days", "values": ["7"]}
        ]
    },
    order_by=[{"property": "raised_time", "order": "desc"}],
    limit=50
)

for item in custom_query.data:
    print(f"Alert {item.get('alert_id')}: {item.get('message')}")

# Query with grouping for aggregation
aggregated_query = client.insights.alerts.query(
    properties=[
        {"property": "severity"},
        {"property": "alert_id", "function": "distinct_count", "alias": "alert_count"}
    ],
    group_by=["severity"],
    filter={
        "rules": [
            {"property": "updated_time", "operator": "last_n_days", "values": ["30"]}
        ]
    }
)
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    AuthenticationError,
    ServerError
)

try:
    alerts = client.insights.alerts.list(
        severity=["invalid_severity"]
    )
except InvalidObjectError as e:
    print(f"Invalid parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except ServerError as e:
    print(f"Server error: {e.message}")
```

## Related Topics

- [Alert Models](../models/insights/alerts_models.md#alert)
- [Insights Overview](index.md)
- [API Client](../client.md)
